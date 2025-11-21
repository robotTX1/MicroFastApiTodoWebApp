from dataclasses import dataclass


@dataclass
class PageInfo:
    size: int
    number: int
    total_elements: int
    total_pages: int