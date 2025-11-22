from fastapi.requests import Request
from yarl import URL

from microfastapitodowebapp.config.oauth import oauth
from microfastapitodowebapp.model.todo_request import TodoShareRequest
from microfastapitodowebapp.model.todo_response import TodoShareResponse

BASE_PATH: str = "/api/v1/todos"


async def get_todo_shares(request: Request, todo_id: int) -> TodoShareResponse:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}/share")
    response = await oauth.keycloak.get(str(url), request=request)
    response.raise_for_status()
    return TodoShareResponse.from_dict(response.json())


async def create_todo_share(request: Request, todo_id: int, todo_share_request: TodoShareRequest) -> None:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}/share")
    response = await oauth.keycloak.put(str(url), json=todo_share_request.model_dump(mode="json"), request=request)
    response.raise_for_status()


async def delete_todo_share(request: Request, todo_id: int, email: str) -> None:
    url = URL.build(path=f"{BASE_PATH}/{todo_id}/share", query={"email": email})
    response = await oauth.keycloak.delete(str(url), request=request)
    response.raise_for_status()
