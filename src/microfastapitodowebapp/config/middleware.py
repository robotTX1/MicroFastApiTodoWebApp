import fnmatch
from datetime import datetime, timezone

from fastapi.requests import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from microfastapitodowebapp.config.context import request_context
from microfastapitodowebapp.config.oauth import oauth
from microfastapitodowebapp.config.configuration import service_config

TOKEN = "token"
AUTH_SERVER_HOST = service_config.get("authorizationServerHost")

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request_context.set(request)
        try:
            response = await call_next(request)
            return response
        finally:
            request_context.reset(token)


class AuthGuardMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, callback_endpoint_name: str, public_urls: list[str]):
        super().__init__(app)
        self.callback_name = callback_endpoint_name
        self.public_urls = public_urls

    def should_skip(self, path: str) -> bool:
        for pattern in self.public_urls:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        if self.should_skip(request.url.path):
            logger.trace("Skipping auth check for {}", request.url.path)
            return await call_next(request)
        session_id = request.cookies.get("session")
        if session_id:
            logger.trace("Session found {}", session_id)
            if TOKEN in request.session:
                logger.trace("Access token found in {}", session_id)
                access_token = request.session[TOKEN]
                now = datetime.now(timezone.utc).timestamp()
                refresh_expires_at = access_token["refresh_expires_at"]
                if refresh_expires_at > now:
                    return await call_next(request)
        logger.trace("User is not authenticated, redirecting to login page")
        if request.headers.get("HX-Request") and request.headers.get("HX-Current-URL"):
            redirect_url = request.headers.get("HX-Current-URL")
        else:
            redirect_url = str(request.url)
        if request.url.query != "":
            redirect_url += "?" + request.url.query
        request.session["redirect_url"] = redirect_url
        redirect_uri = request.url_for('auth_callback')
        return await oauth.keycloak.authorize_redirect(request, redirect_uri)


class HTMXRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.headers.get("HX-Request"):
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("location")
                if AUTH_SERVER_HOST in location:
                    new_response = Response(status_code=200)
                    new_response.headers["HX-Redirect"] = location
                    cookie_val = response.headers.get("set-cookie")
                    if cookie_val:
                        new_response.headers["set-cookie"] = cookie_val
                    return new_response
        return response