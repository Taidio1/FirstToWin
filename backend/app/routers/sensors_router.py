import secrets

from sqlalchemy.orm import Session
from app.db.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.db.entities import Sensor, User
from app.models.sensor_model import create_sensor_request
router = APIRouter()


@router.get("")
def get(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    '''
    Returns list of all sensors
    '''
    return db.query(Sensor).all()


@router.post("", status_code=201)
def create(
        req: create_sensor_request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    '''
    Creates a sensor
    '''
    sensor = Sensor(
        name=req.name,
        location=req.location,
        status=req.status,
        api_key=secrets.token_hex(32),
    )

    db.add(sensor)
    db.commit()
    db.refresh(sensor)

    return sensor


@router.delete("/{id}")
def delete(
        id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    '''
    Delete a sensor by id
    '''

    sensor = db.get(Sensor, id)
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    db.delete(sensor)
    db.commit()

    return {"message": "Sensor deleted"}
