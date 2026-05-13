from typing import Literal
from app.models.user_model import User
from pydantic import BaseModel


class login_response(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
    user: User


class login_request(BaseModel):
    email: str
    password: str


class register_request(BaseModel):
    email: str
    username: str
    password: str
