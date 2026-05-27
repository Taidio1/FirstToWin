from dataclasses import dataclass
from typing import Literal
from datetime import datetime


@dataclass
class User:
    id: int
    email: str
    username: str
    role: Literal["admin", "user"]
    created_at: datetime
    password: str | None
