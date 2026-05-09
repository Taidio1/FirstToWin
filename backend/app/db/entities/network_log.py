from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from app.db.db import Base
from datetime import datetime

class NetworkLog(Base):
    __tablename__ = "network_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[str] = mapped_column(String)
    src_ip: Mapped[str] = mapped_column(String)
    dst_ip: Mapped[str] = mapped_column(String)
    src_port: Mapped[str] = mapped_column(String)
    dst_port: Mapped[str] = mapped_column(String)
    protocol: Mapped[str] = mapped_column(String)
    flags: Mapped[str] = mapped_column(String)
    payload_size: Mapped[int] = mapped_column(Integer)