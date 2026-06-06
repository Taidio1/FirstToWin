from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.middleware.auth import get_current_user
from app.services import reports

router = APIRouter()


@router.get("/top-ips")
def report_top_ips(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return reports.top_suspicious_ips(db)


@router.get("/rules")
def report_rules(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return reports.rules_summary(db)


@router.get("/scenarios")
def report_scenarios(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return reports.scenario_summary(db)
