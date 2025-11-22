from dataclasses import dataclass


@dataclass
class PageInfo:
    size: int
    number: int
    total_elements: int
    total_pages: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            size=data["size"],
            number=data["number"],
            total_elements=data["totalElements"],
            total_pages=data["totalPages"]
        )
