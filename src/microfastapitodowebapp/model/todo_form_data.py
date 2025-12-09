from typing import List, Optional
from dataclasses import dataclass
from fastapi import Form


@dataclass
class TodoFormData:
    title: str = Form(...)
    description: str = Form("")
    priority: int = Form(0)
    completed: bool = Form(False)
    deadline_date: Optional[str] = Form(None)
    deadline_time: Optional[str] = Form(None)
    categories: Optional[List[str]] = Form(None)
    shares_email: Optional[List[str]] = Form(None)
    shares_access_level: Optional[List[int]] = Form(None)