from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, cast, String
from app.db.entities import NetworkLog
from app.db.db import get_db
from app.middleware.auth import get_current_user
router = APIRouter()


@router.get("")
def get_logs(page: int = Query(1, ge=1),
             page_size: int = Query(20, ge=1),
             q: str | None = None,
             db: Session = Depends(get_db),
             User=Depends(get_current_user)
             ):
    '''
    Gets paginated list logs, queried by 'q'.
    This is slow af
    '''
    query = select(NetworkLog)

    if q:
        query = query.where(
            or_(
                cast(NetworkLog.sensor_id, String).ilike(q),
                cast(NetworkLog.timestamp, String).ilike(q),
                NetworkLog.src_ip.ilike(q),
                NetworkLog.dst_ip.ilike(q),
                NetworkLog.src_port.ilike(q),
                NetworkLog.dst_port.ilike(q),
                cast(NetworkLog.protocol, String).ilike(q),
                NetworkLog.flags.ilike(q),
                cast(NetworkLog.payload_size, String).ilike(q),
            )
        )

    total = db.scalar(
        select(func.count())
        .select_from(query.subquery())
    )

    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(NetworkLog.timestamp.desc())
    )

    logs = db.execute(query).scalars().all()

    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size
    }
