from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

from microfastapitodowebapp.domain.priority import priority_levels


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
