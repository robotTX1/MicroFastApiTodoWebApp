from asyncio import sleep
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from microfastapitodowebapp.config.jinja import templates
from microfastapitodowebapp.domain.query import QueryMode, TodoQuery
from microfastapitodowebapp.model.todo_response import TodoResponse, TodoStatistics
from microfastapitodowebapp.service import todo as todo_service, statistics as statistics_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(path="", name="dashboard", response_class=HTMLResponse)
async def get_landing_page(request: Request):
    token = request.session["token"]
    userinfo = token["userinfo"]
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={"name": userinfo["given_name"]}
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
    return templates.TemplateResponse(
        request=request, name="partials/_todo_list.html", context={"todos": todo_response.content}
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
