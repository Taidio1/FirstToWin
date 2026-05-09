from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.db import Base
from datetime import datetime

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
    created_at: Mapped[str] = mapped_column(String)