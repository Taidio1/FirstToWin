from pydantic import BaseModel
from typing import Literal


class match(BaseModel):
    src_ip: str | None = None
    dst_ip: str | None = None
    dst_port: int | None = None
    protocol: Literal["TCP", "UDP", "ICMP", "OTHER"]
    threshold: int | None = None
    window_seconds: int | None = None


class create_rule_request(BaseModel):
    name: str
    type: Literal["blacklist_ip", "blacklist_ip",
                  "connection_threshold", "port_scan", "protocol_filter"]
    enabled: bool
    severity: Literal["critical", "high", "medium", "low", "info"]
    match: match
    description: str


class MatchResponse(BaseModel):
    src_ip: str | None
    dst_ip: str | None
    dst_port: int | None
    protocol: str
    threshold: int | None
    window_seconds: int | None

    class Config:
        from_attributes = True


class RuleResponse(BaseModel):
    id: int
    name: str
    type: str
    enabled: bool
    severity: str
    description: str

    match: MatchResponse | None

    class Config:
        from_attributes = True
