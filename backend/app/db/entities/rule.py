from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Enum, ForeignKey
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


class ProtocolEnum(str, enum.Enum):
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    OTHER = "OTHER"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(
        ForeignKey("rules.id"),
        unique=True,
        nullable=False
    )
    rule: Mapped["Rule"] = relationship(
        "Rule",
        back_populates="match"
    )

    src_ip: Mapped[str | None] = mapped_column(String, nullable=True)
    dst_ip: Mapped[str | None] = mapped_column(String, nullable=True)

    dst_port: Mapped[int | None] = mapped_column(Integer, nullable=True)

    protocol: Mapped[ProtocolEnum] = mapped_column(
        Enum(ProtocolEnum),
        nullable=False
    )

    threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)

    window_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[RuleType] = mapped_column(
        Enum(RuleType), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    match = relationship("Match", back_populates="rule",
                         uselist=False, cascade="all, delete-orphan")
