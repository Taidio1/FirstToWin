from pydantic import BaseModel
from app.shared_models import Severity, AlertStatus


class paginated_alerts_request(BaseModel):
    page: int
    page_size: int
    severity: Severity
    status: AlertStatus
    q: str


class alert_patch_request(BaseModel):
    status: AlertStatus
