import fnmatch
from datetime import datetime, timezone

from fastapi.requests import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from microfastapitodowebapp.config.context import request_context
from microfastapitodowebapp.config.oauth import oauth

TOKEN = "token"


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
        redirect_url = request.url.path
        if request.url.query != "":
            redirect_url += "?" + request.url.query
        request.session["redirect_url"] = redirect_url
        redirect_uri = request.url_for('auth_callback')
        return await oauth.keycloak.authorize_redirect(request, redirect_uri)
