from dataclasses import dataclass
from typing import List

from microfastapitodowebapp.model.page_info import PageInfo
from microfastapitodowebapp.model.todo import Todo


@dataclass
class TodoResponse():
    content: List[Todo]
    page: PageInfo

    @classmethod
    def from_json(cls, data: dict):
        todos = [Todo.from_dict(item) for item in data["content"]]
        page_data = data["page"]
        page_info = PageInfo(
            size=page_data["size"],
            number=page_data["number"],
            total_elements=page_data["totalElements"],
            total_pages=page_data["totalPages"]
        )
        return cls(content=todos, page=page_info)
