import enum


class SensorStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    degraded = "degraded"
