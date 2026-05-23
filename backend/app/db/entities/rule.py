from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String, Integer, Boolean, Enum, ForeignKey, func
from app.db.db import Base
from app.shared_models import Protocol, Severity, RuleType


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

    protocol: Mapped[Protocol] = mapped_column(
        Enum(Protocol),
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    match = relationship("Match", back_populates="rule",
                         uselist=False, cascade="all, delete-orphan")
