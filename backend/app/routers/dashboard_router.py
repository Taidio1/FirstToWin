from sqlalchemy.orm import Session
from app.db.db import get_db
from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from sqlalchemy import select, func
from app.db.entities import Alert
from app.shared_models import Severity
from datetime import datetime, timedelta
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
    from_date = datetime.now() - timedelta(hours=24)
    query_alerts_24 = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.created_at > from_date)
    )
    alerts_24 = db.execute(query_alerts_24).scalar()

    query_critical_alerts = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.severity == Severity.critical)
    )
    critical_alerts = db.execute(query_critical_alerts).scalar()

    return {
        "last_24h_alerts": alerts_24,
        "critical_alerts": critical_alerts
    }
