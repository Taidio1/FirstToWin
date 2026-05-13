from pydantic import BaseModel
from app.shared_models import SensorStatus


class create_sensor_request(BaseModel):
    name: str
    location: str
    status: SensorStatus
