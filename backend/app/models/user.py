from dataclasses import dataclass
from typing import Literal
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    username: str
    role: Literal["admin", "analyst", "viewer"]
    created_at: datetime

