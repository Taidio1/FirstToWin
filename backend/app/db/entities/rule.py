from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean
from app.db.db import Base
import enum


class RuleType(str, enum.Enum):
    blacklist_ip = "blacklist_ip"
    connection_threshold = "connection_threshold"
    port_scan = "port_scan"
    protocol_filter = "protocol_filter"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[enum.Enum] = mapped_column(
        enum.Enum(RuleType), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[enum.Enum] = mapped_column(
        enum.Enum(Severity), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    match = relationship("RuleMatch", back_populates="rule",
                         uselist=False, cascade="all, delete")
