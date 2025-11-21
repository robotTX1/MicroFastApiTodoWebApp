from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from microfastapitodowebapp.config.jinja import templates

router = APIRouter(tags=["landing"])


@router.get("/", name="landing", response_class=HTMLResponse)
async def get_landing_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="landing.html"
    )
