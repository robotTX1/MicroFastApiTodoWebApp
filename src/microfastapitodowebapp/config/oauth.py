import time

from authlib.integrations.starlette_client import OAuth
from loguru import logger
from starlette.requests import Request

from microfastapitodowebapp.config.configuration import service_config, secrets
from microfastapitodowebapp.config.context import request_context


async def fetch_token(request: Request):
    logger.trace("Fetching token from session {}", request.cookies.get("session"))
    token = request.session.get("token")
    return dict(
        access_token=token["access_token"],
        token_type=token["token_type"],
        refresh_token=token["refresh_token"],
        expires_at=token["expires_at"],
    )


async def update_token(token, access_token=None, refresh_token=None):
    logger.trace("Session access token expired")
    session = request_context.get().session
    userinfo = session["token"]["userinfo"]
    token["userinfo"] = userinfo
    token["refresh_expires_at"] = int(time.time()) + token["expires_in"]
    session["token"] = token


oauth = OAuth()
oauth.register(
    name="keycloak",
    client_id=service_config.get("applicationClientId"),
    client_secret=secrets.get(service_config.get("applicationClientSecretName")),
    server_metadata_url=service_config.get("authorizationServerMetaDataUrl"),
    access_token_url=service_config.get("authorizationServerTokenUri"),
    refresh_token_url=service_config.get("authorizationServerTokenUri"),
    authorize_url=service_config.get("authorizationServerUri"),
    api_base_url=service_config.get("todoApiBaseUrl"),
    jwks_uri=service_config.get("authorizationServerJwksUri"),
    fetch_token=fetch_token,
    update_token=update_token,
    client_kwargs={
        "scope": "openid email profile",
        "code_challenge_method": "S256"
    }
)
