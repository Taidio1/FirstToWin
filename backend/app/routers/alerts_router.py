from app.models.alert_model import alert_patch_request
from fastapi import APIRouter, Query, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.entities.alert import Alert
from app.middleware.auth import get_current_user
from app.services.realtime_alerts import alert_broadcaster
from app.shared_models import AlertStatus, Severity
router = APIRouter()


@router.websocket("/ws")
async def alert_websocket(websocket: WebSocket):
    await alert_broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        alert_broadcaster.disconnect(websocket)


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

    if q:
        query = query.filter(
            or_(
                Alert.rule_name.ilike(f"%{q}%"),
                Alert.details.ilike(f"%{q}%"),
                Alert.src_ip.ilike(f"%{q}%"),
                Alert.dst_ip.ilike(f"%{q}%"),
            )
        )

    total = query.count()
    offset = (page - 1) * page_size

    alerts = (
        query
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": alerts,
        "total": total,
        "page": page,
        "page_size": page_size
    }


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

    return alert
