from sqlalchemy.orm import Session
from app.db.db import get_db
from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
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
    return
