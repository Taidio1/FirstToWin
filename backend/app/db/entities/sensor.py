from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Enum
from app.db.db import Base
from app.shared_models import SensorStatus


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    status: Mapped[SensorStatus] = mapped_column(
        Enum(SensorStatus), nullable=False)
