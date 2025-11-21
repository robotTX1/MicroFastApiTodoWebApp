from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

from microfastapitodowebapp.config.jinja import templates
from microfastapitodowebapp.model.todo_response import TodoResponse
from microfastapitodowebapp.service import todo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get(path="", name="dashboard", response_class=HTMLResponse)
async def get_landing_page(request: Request):
    token = request.session["token"]
    userinfo = token["userinfo"]

    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={"name": userinfo["family_name"]}
    )

@router.get(path="/partials/todos", name="dashboard_todos", response_class=HTMLResponse)
async def get_partial_todos(request: Request):
    todo_response: TodoResponse = await todo.get_todos(request)
    return templates.TemplateResponse(
        request=request, name="partials/_todo_list.html", context={"todos": todo_response.content}
    )
