import time

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from microfastapitodowebapp.config.oauth import oauth

router = APIRouter(prefix="/login", tags=["auth"])

@router.get("")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    request.session["redirect_url"] = "/"
    return await oauth.keycloak.authorize_redirect(request, redirect_uri)


@router.get("/oauth2/code/keycloak", name="auth_callback")
async def auth_callback(request: Request):
    token = await oauth.keycloak.authorize_access_token(request)
    token["refresh_expires_at"] = int(time.time())+ token["refresh_expires_in"]
    request.session['token'] = token
    redirect_url = request.session["redirect_url"]
    request.session.pop("redirect_url")
    return RedirectResponse(url=redirect_url)