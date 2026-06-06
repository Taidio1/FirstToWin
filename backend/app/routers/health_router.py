from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.db import get_db

router = APIRouter()


@router.get("")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("select 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "database": "error", "version": "0.0.1-dev"},
        ) from exc

    return {
        "status": "ok",
        "database": "ok",
        "version": "0.0.1-dev",
    }
