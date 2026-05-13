from app.models.alert_model import alert_patch_request
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.entities.alert import Alert
from app.middleware.auth import get_current_user
from app.shared_models import AlertStatus, Severity
router = APIRouter()


@router.get("")
def paginated_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),

    severity: Severity | None = None,

    status: AlertStatus | None = None,

    q: str | None = None,
    db: Session = Depends(get_db),
    User=Depends(get_current_user)
):
    '''
    Get paginated list of alerts
    '''
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)

    if status:
        query = query.filter(Alert.status == status)

    offset = (page - 1) * page_size

    alerts = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return alerts


@router.get("/{id}")
def alert(
    id: int,
    db: Session = Depends(get_db),
    User=Depends(get_current_user)
):
    '''
    Get alert details by id
    '''
    alert = db.query(Alert).filter(Alert.id == id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.get("/{id}/osint")
def alert_osint(id: int, User=Depends(get_current_user)):
    '''
    Get alert's related OSINT data by id
    OSINT sources:
    - AbuseIPDB
    - VirusTotal
    '''
    return {"message": "alert osint"}


@router.patch("/{id}")
def update_alert(
    req: alert_patch_request,
    id: int,
    db: Session = Depends(get_db),
    User=Depends(get_current_user)
):
    '''
    Update alert status:
    - "open"
    - "acknowledged"
    - "resolved"
    '''
    alert = db.get(Alert, id)
    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    update_data = req.model_dump(exclude_unset=True)

    for k, v in update_data.items():
        setattr(alert, k, v)

    db.commit()
    db.refresh(alert)

    return
