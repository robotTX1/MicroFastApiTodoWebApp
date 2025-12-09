from datetime import datetime
from typing import List


from pydantic import BaseModel, Field


class BaseTodoRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    completed: bool | None = None
    parent: int | None = None
    priority: int | None = 0
    categories: List[str] | None = None


class TodoCreateRequest(BaseTodoRequest):
    completed: bool = False
    priority: int = 0
    categories: List[str] = Field(default_factory=list)
    pass


class TodoUpdateRequest(BaseTodoRequest):
    pass


class TodoPatchRequest(BaseTodoRequest):
    pass


class TodoPatchNoDateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    parent: int | None = None
    priority: int | None = 0
    categories: List[str] | None = None


class TodoShareRequest(BaseModel):
    email: str
    accessLevel: int
