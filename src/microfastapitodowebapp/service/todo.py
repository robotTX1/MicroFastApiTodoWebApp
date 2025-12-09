from fastapi.requests import Request
from yarl import URL

from microfastapitodowebapp.config.oauth import oauth
from microfastapitodowebapp.domain.query import TodoQuery, QueryMode
from microfastapitodowebapp.model.todo_request import TodoCreateRequest, TodoUpdateRequest, TodoPatchRequest, TodoPatchNoDateRequest
from microfastapitodowebapp.model.todo_response import TodoResponse, Todo
from microfastapitodowebapp.util.url_helper import build_url

BASE_PATH: str = "/api/v1/todos"


async def get_todos(request: Request, query: TodoQuery = TodoQuery(),
                    query_mode: QueryMode = QueryMode.ALL) -> TodoResponse:
    url = build_url(BASE_PATH, query, query_mode)
    response = await oauth.keycloak.get(str(url), request=request)
    response.raise_for_status()
    return TodoResponse.from_dict(response.json())


async def get_todo_by_id(request: Request, todo_id: int) -> Todo:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}")
    response = await oauth.keycloak.get(str(url), request=request)
    response.raise_for_status()
    return Todo.from_dict(response.json())


async def create_todo(request: Request, todo: TodoCreateRequest) -> Todo:
    response = await oauth.keycloak.post(BASE_PATH, json=todo.model_dump(mode="json"), request=request)
    response.raise_for_status()
    return Todo.from_dict(response.json())


async def update_todo(request: Request, todo_id: int, todo: TodoUpdateRequest) -> Todo:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}")
    response = await oauth.keycloak.put(str(url), json=todo.model_dump(mode="json"), request=request)
    response.raise_for_status()
    return Todo.from_dict(response.json())


async def patch_todo(request: Request, todo_id: int, todo: TodoPatchRequest | TodoPatchNoDateRequest) -> Todo:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}")
    response = await oauth.keycloak.patch(str(url), json=todo.model_dump(mode="json"), request=request)
    response.raise_for_status()
    return Todo.from_dict(response.json())


async def delete_todo(request: Request, todo_id: int) -> None:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}")
    response = await oauth.keycloak.delete(str(url), request=request)
    response.raise_for_status()
