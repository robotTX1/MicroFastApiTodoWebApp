from fastapi.requests import Request

from microfastapitodowebapp.config.oauth import oauth
from microfastapitodowebapp.model.todo_response import TodoResponse


async def get_todos(request: Request) -> TodoResponse:
    response = await oauth.keycloak.get("/api/v1/todos", request=request)
    response.raise_for_status()
    return TodoResponse.from_json(response.json())
