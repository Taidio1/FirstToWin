from pydantic import BaseModel
from app.shared_models import Severity, RuleType, Protocol


class match(BaseModel):
    src_ip: str | None = None
    dst_ip: str | None = None
    dst_port: int | None = None
    protocol: Protocol
    threshold: int | None = None
    window_seconds: int | None = None


class create_rule_request(BaseModel):
    name: str
    type: RuleType
    enabled: bool
    severity: Severity
    match: match
    description: str


class MatchResponse(BaseModel):
    src_ip: str | None
    dst_ip: str | None
    dst_port: int | None
    protocol: Protocol
    threshold: int | None
    window_seconds: int | None

    class Config:
        from_attributes = True


class RuleResponse(BaseModel):
    id: int
    name: str
    type: str
    enabled: bool
    severity: Severity
    description: str

    match: MatchResponse | None

    class Config:
        from_attributes = True
