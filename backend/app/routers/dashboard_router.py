from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.db.entities import Alert, NetworkLog, Sensor
from app.middleware.auth import get_current_user
from app.shared_models import AlertStatus, SensorStatus, Severity
router = APIRouter()


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    User=Depends(get_current_user)
):
    '''
    Returns:
    - count of:
        - alerts from last 24 hours
        - open critical alerts
        - sensors online
    - severity pie chart
    - severity linear timeline
    - list of top sources
    '''
    from_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
    alerts_24h = db.scalars(
        select(Alert).where(Alert.created_at >= from_date)
    ).all()
    logs_24h = db.scalars(
        select(NetworkLog).where(NetworkLog.timestamp >= from_date)
    ).all()

    open_alerts = [a for a in alerts_24h if a.status == AlertStatus.open.value]
    severity_counts = Counter(a.severity for a in alerts_24h)
    source_counts = Counter(a.src_ip for a in alerts_24h)
    source_severity: dict[str, str] = {}
    severity_rank = {
        Severity.info.value: 0,
        Severity.low.value: 1,
        Severity.medium.value: 2,
        Severity.high.value: 3,
        Severity.critical.value: 4,
    }
    for alert in alerts_24h:
        current = source_severity.get(alert.src_ip, Severity.info.value)
        if severity_rank.get(alert.severity, 0) >= severity_rank.get(current, 0):
            source_severity[alert.src_ip] = alert.severity

    timeline = []
    for i in range(23, -1, -1):
        hour_start = datetime.now(timezone.utc).replace(
            tzinfo=None, minute=0, second=0, microsecond=0
        ) - timedelta(hours=i)
        hour_end = hour_start + timedelta(hours=1)
        timeline.append({
            "hour": hour_start.isoformat(),
            "count": sum(1 for a in alerts_24h if hour_start <= a.created_at.replace(tzinfo=None) < hour_end)
        })

    return {
        "alerts_24h": len(alerts_24h),
        "alerts_open": len(open_alerts),
        "alerts_critical_open": sum(
            1 for a in open_alerts if a.severity == Severity.critical.value
        ),
        "sensors_online": db.scalar(
            select(func.count()).select_from(Sensor).where(Sensor.status == SensorStatus.online)
        ) or 0,
        "sensors_total": db.scalar(select(func.count()).select_from(Sensor)) or 0,
        "packets_24h": len(logs_24h),
        "by_severity": [
            {"severity": severity.value, "count": severity_counts.get(severity.value, 0)}
            for severity in Severity
        ],
        "alerts_timeline": timeline,
        "top_sources": [
            {
                "ip": ip,
                "count": count,
                "severity": source_severity.get(ip, Severity.info.value),
            }
            for ip, count in source_counts.most_common(5)
        ],
    }
