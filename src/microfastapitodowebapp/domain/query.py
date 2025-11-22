from dataclasses import dataclass
from enum import Enum


@dataclass
class TodoQuery:
    search: str = None
    sort: str = None
    page_number: int = None
    page_size: int = None

    def to_dict(self):
        result = {}
        if self.search:
            result["search"] = self.search
        if self.sort:
            result["sort"] = self.sort
        if self.page_number:
            result["pageNumber"] = self.page_number
        if self.page_size:
            result["pageSize"] = self.page_size
        return result

class QueryMode(Enum):
    ALL = "ALL",
    SHARED = "SHARED",
    OWN = "OWN"