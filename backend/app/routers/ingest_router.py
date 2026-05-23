from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.db.entities import NetworkLog, Sensor
from app.models.ingest_model import ingest_log_request
from app.services.demo_seed import ensure_demo_data
from app.services.detection_engine import detect_alerts

router = APIRouter()


@router.post("/logs", status_code=status.HTTP_201_CREATED)
def ingest_log(req: ingest_log_request, db: Session = Depends(get_db)):
    sensor = ensure_demo_data(db)
    if req.sensor_name != sensor.name:
        sensor = Sensor(name=req.sensor_name, location="local ingest", status="online")
        db.add(sensor)
        db.commit()
        db.refresh(sensor)

    log = NetworkLog(
        sensor_id=sensor.id,
        timestamp=req.timestamp or datetime.now(timezone.utc),
        src_ip=req.src_ip,
        dst_ip=req.dst_ip,
        src_port=str(req.src_port),
        dst_port=str(req.dst_port),
        protocol=req.protocol,
        flags=req.flags,
        payload_size=req.payload_size,
    )
    db.add(log)
    db.flush()

    alerts = detect_alerts(db, log, sensor.name)
    db.commit()
    db.refresh(log)
    for alert in alerts:
        db.refresh(alert)

    return {"log": log, "alerts": alerts}
