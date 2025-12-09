from typing import Annotated

from fastapi import APIRouter, Query, Depends
from fastapi.responses import HTMLResponse

from microfastapitodowebapp.domain.query import QueryMode, TodoQuery
from microfastapitodowebapp.util.todo_form_helper import *
from microfastapitodowebapp.model.todo_response import TodoResponse, TodoStatistics
from microfastapitodowebapp.service import (
    todo as todo_service,
    statistics as statistics_service,
    share as share_service
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(path="", name="dashboard", response_class=HTMLResponse)
async def get_landing_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboard/index.html"
    )


@router.get(path="/partials/content", name="dashboard_content", response_class=HTMLResponse)
async def get_partial_content(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboard/content.html"
    )


@router.get(path="/partials/todos", name="dashboard_todos", response_class=HTMLResponse)
async def get_partial_todos(request: Request,
                            search: str = None,
                            sort: str = None,
                            mode: QueryMode = QueryMode.OWN,
                            page_number: Annotated[int | None, Query(alias="pageNumber")] = 0,
                            page_size: Annotated[int | None, Query(alias="pageSize")] = 20):
    query = TodoQuery(search, sort, page_number, page_size)
    todo_response: TodoResponse = await todo_service.get_todos(request, query, mode)
    new_url = str(request.url_for("dashboard").include_query_params(**request.query_params))
    return templates.TemplateResponse(
        request=request, name="partials/_todo_list.html",
        context={"todos": todo_response.content, "page": todo_response.page},
        headers={"HX-Push-Url": new_url}
    )


@router.get(path="/partials/statistics", name="dashboard_statistics", response_class=HTMLResponse)
async def get_partial_statistics(request: Request,
                                 search: str = None,
                                 sort: str = None,
                                 mode: QueryMode = QueryMode.OWN,
                                 page_number: Annotated[int | None, Query(alias="pageNumber")] = 0,
                                 page_size: Annotated[int | None, Query(alias="pageSize")] = 20):
    query = TodoQuery(search, sort, page_number, page_size)
    todo_statistics: TodoStatistics = await statistics_service.get_simple_stats(request, query, mode)
    return templates.TemplateResponse(
        request=request, name="partials/_todo_statistics.html", context={"statistics": todo_statistics}
    )


@router.get("/partials/drawer/new", response_class=HTMLResponse)
async def get_new_todo_drawer(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/_drawer_content.html",
        context={"todo": None}
    )


@router.get("/partials/drawer/{todo_id}", response_class=HTMLResponse)
async def get_edit_todo_drawer(request: Request, todo_id: int):
    todo_item = await todo_service.get_todo_by_id(request, todo_id)
    shares = await share_service.get_todo_shares(request, todo_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/_drawer_content.html",
        context={"todo": todo_item, "share": shares}
    )


@router.post("/todos/create", response_class=HTMLResponse)
async def create_todo_from_form(request: Request,
                                form_data: Annotated[TodoFormData, Depends()]):
    try:
        todo_data = build_create_request(form_data)
        new_todo = await todo_service.create_todo(request, todo_data)

        return create_toast_response(request, await create_shares_from_form(
            request=request,
            todo_id=new_todo.id,
            shares_email=form_data.shares_email,
            shares_access_level=form_data.shares_access_level,
            skip_first=False,
        ))

    except Exception as e:
        print(f"Error creating todo: {e}")
        return create_toast_response(request, is_error=True)


@router.post("/todos/update/{todo_id}", response_class=HTMLResponse)
async def update_todo_from_form(request: Request,
                                todo_id: int,
                                form_data: Annotated[TodoFormData, Depends()]):
    try:
        todo_data = build_patch_request(form_data)
        await todo_service.patch_todo(request, todo_id, todo_data)

        return create_toast_response(request, await sync_shares_from_form(
            request=request,
            todo_id=todo_id,
            shares_email=form_data.shares_email,
            shares_access_level=form_data.shares_access_level,
            skip_first=True,
        ))

    except Exception as e:
        print(f"Error updating todo: {e}")
        return create_toast_response(request, is_error=True)


@router.delete("/todos/{todo_id}", response_class=HTMLResponse)
async def delete_todo_item(request: Request, todo_id: int):
    try:
        await todo_service.delete_todo(request, todo_id)
        return create_toast_response(request, custom_message="Todo deleted.")

    except Exception as e:
        print(f"Error deleting todo: {e}")
        return create_toast_response(request, is_error=True,
                                     custom_message="Unable to delete the todo. Please try again.")
