from fastapi import APIRouter, Depends
from app.models.rule_model import create_rule_request, update_rule_request
from sqlalchemy.orm import Session
from app.db.db import get_db

router = APIRouter()


@router.get("")
def get(db: Session = Depends(get_db)):
    '''
    Get all rules
    '''
    return db.query(Rule).all()


@router.post("")
def create(req: create_rule_request, db: Session = Depends(get_db)):
    '''
    Create a new rule
    '''
    return


@router.put("/{id}")
def update(id: int, req: create_rule_request, db: Session = Depends(get_db)):
    '''
    Update an existing rule
    '''
    return


@router.delete("/{id}")
def delete(id: int):
    '''
    Delete a rule
    '''
    return
