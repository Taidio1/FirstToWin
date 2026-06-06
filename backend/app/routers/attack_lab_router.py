from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.db.entities import User
from app.middleware.auth import get_current_user, require_admin
from app.services import attack_lab

router = APIRouter()


class RunRequest(BaseModel):
    scenario: str


class AutoStartRequest(BaseModel):
    interval_seconds: int = Field(default=30, ge=5, le=3600)


@router.get("/status")
def get_status(user: User = Depends(get_current_user)):
    return attack_lab.get_status()


@router.post("/run", status_code=status.HTTP_200_OK)
def run_scenario(
    req: RunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    if req.scenario not in attack_lab.ALLOWED_SCENARIOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown scenario. Allowed: {attack_lab.ALLOWED_SCENARIOS}",
        )
    return attack_lab.run_scenario(db, req.scenario)


@router.post("/auto/start", status_code=status.HTTP_200_OK)
async def start_auto(req: AutoStartRequest, user: User = Depends(require_admin)):
    attack_lab.start_auto(req.interval_seconds)
    return attack_lab.get_status()


@router.post("/auto/stop", status_code=status.HTTP_200_OK)
async def stop_auto(user: User = Depends(require_admin)):
    attack_lab.stop_auto()
    return attack_lab.get_status()
