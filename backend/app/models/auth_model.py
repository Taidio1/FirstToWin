from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from app.models.user_model import User

@dataclass
class login_response:
    access_token: str
    token_type: Literal["bearer"]
    user: User


@dataclass
class login_request:
    email: str
    password: str


@dataclass
class register_request:
    email: str
    username: str
    password: str
