from datetime import datetime

from pydantic import BaseModel, Field

from app.shared_models import Protocol


class ingest_log_request(BaseModel):
    sensor_name: str = Field(default="local-demo-sensor")
    timestamp: datetime | None = None
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: Protocol = Protocol.TCP
    flags: str = ""
    payload_size: int = 0
