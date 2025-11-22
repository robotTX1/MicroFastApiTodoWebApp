from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from microfastapitodowebapp.domain.priority import priority_levels
from microfastapitodowebapp.model.page_info import PageInfo


@dataclass
class Todo:
    id: int
    title: Optional[str]
    description: Optional[str]
    deadline: Optional[datetime]
    completed: bool
    parent_id: Optional[int]
    shared: bool
    priority: int
    categories: List[str]
    access_level: int
    created_at: datetime
    updated_at: datetime

    @property
    def priority_text(self):
        return priority_levels.get(self.priority, "Unknown")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            deadline=datetime.fromisoformat(data.get("deadline")) if data.get("deadline") else None,
            completed=data.get("completed"),
            parent_id=data.get("parent_id"),
            shared=data.get("shared"),
            priority=data.get("priority"),
            categories=data.get("categories", []),
            access_level=data.get("accessLevel"),
            created_at=datetime.fromisoformat(data.get("createdAt")),
            updated_at=datetime.fromisoformat(data.get("updatedAt")),
        )


@dataclass
class TodoShare:
    email: str
    access_level: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            email=data.get("email"),
            access_level=data.get("accessLevel"),
        )


@dataclass
class TodoResponse:
    content: List[Todo]
    page: PageInfo

    @classmethod
    def from_dict(cls, data: dict):
        todos = [Todo.from_dict(item) for item in data["content"]]
        page_info = PageInfo.from_dict(data["page"])
        return cls(content=todos, page=page_info)


@dataclass
class TodoShareResponse:
    content: List[TodoShare]
    page: PageInfo

    @classmethod
    def from_dict(cls, data: dict):
        shares = [TodoShare.from_dict(item) for item in data["content"]]
        page_info = PageInfo.from_dict(data["page"])
        return cls(content=shares, page=page_info)


@dataclass
class TodoStatistics:
    total: int
    finished: int
    unfinished: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            total=data.get("total"),
            finished=data.get("finished"),
            unfinished=data.get("unfinished"),
        )


@dataclass
class GroupedTodoStatistics:
    statistics: Dict[str, TodoStatistics] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        stats = {item: TodoStatistics.from_dict(stats) for  item, stats in data.items()}
        return GroupedTodoStatistics(statistics=stats)
