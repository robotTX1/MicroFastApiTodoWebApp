from fastapi.requests import Request

from microfastapitodowebapp.config.oauth import oauth
from microfastapitodowebapp.domain.query import TodoQuery, QueryMode
from microfastapitodowebapp.model.todo_response import TodoStatistics, GroupedTodoStatistics
from microfastapitodowebapp.util.url_helper import build_url

BASE_PATH: str = "/api/v1/todos/statistics"


async def get_simple_stats(request: Request, query: TodoQuery = TodoQuery(),
                           query_mode: QueryMode = QueryMode.ALL) -> TodoStatistics:
    url = build_url(BASE_PATH, query, query_mode)
    response = await oauth.keycloak.get(url, request=request)
    response.raise_for_status()
    return TodoStatistics.from_dict(response.json())


async def get_grouped_stats(request: Request, group_by: str, query: TodoQuery = TodoQuery(),
                            query_mode: QueryMode = QueryMode.ALL) -> GroupedTodoStatistics:
    url = build_url(BASE_PATH, query, query_mode, {"groupBy": group_by})
    response = await oauth.keycloak.get(url, request=request)
    response.raise_for_status()
    return GroupedTodoStatistics.from_dict(response.json())
