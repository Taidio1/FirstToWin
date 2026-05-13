from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Enum
from app.db.db import Base
from datetime import datetime
from app.shared_models import Protocol


class NetworkLog(Base):
    __tablename__ = "network_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    src_ip: Mapped[str] = mapped_column(String)
    dst_ip: Mapped[str] = mapped_column(String)
    src_port: Mapped[str] = mapped_column(String)
    dst_port: Mapped[str] = mapped_column(String)
    protocol: Mapped[Protocol] = mapped_column(Enum(Protocol))
    flags: Mapped[str] = mapped_column(String)
    payload_size: Mapped[int] = mapped_column(Integer)
