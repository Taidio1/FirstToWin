from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from app.models.user_model import User
from pydantic import BaseModel


class paginated_alerts_request(BaseModel):
    page: int
    page_size: int
    severity: Literal["critical", "high", "medium", "low", "info"]
    status: Literal["open", "acknowledged", "resolved"]
    q: str

class alert_patch_request(BaseModel):
    status: Literal["open", "acknowledged", "resolved"]
