from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from app.db.db import Base
from datetime import datetime, timezone


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(Integer)
    rule_name: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    src_ip: Mapped[str] = mapped_column(String)
    dst_ip: Mapped[str] = mapped_column(String)
    protocol: Mapped[str] = mapped_column(String)
    sensor_id: Mapped[str] = mapped_column(String)
    details: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    fingerprint: Mapped[str] = mapped_column(String, nullable=False, default="")
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
