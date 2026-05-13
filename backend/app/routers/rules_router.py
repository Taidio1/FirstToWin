from fastapi import APIRouter, Depends, HTTPException
from app.models.rule_model import create_rule_request
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.entities import Rule, User, Match
from app.middleware.auth import get_current_user
from app.shared_models import Protocol, Severity, RuleType
router = APIRouter()


@router.get("")
def get(db: Session = Depends(get_db),
        user: User = Depends(get_current_user)):
    '''
    Get all rules
    '''
    return db.query(Rule).all()


@router.post("")
def create(req: create_rule_request,
           db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    '''
    Create a new rule
    '''

    match = Match(
        src_ip=req.match.src_ip,
        dst_ip=req.match.dst_ip,
        dst_port=req.match.dst_port,
        protocol=Protocol(req.match.protocol),
        threshold=req.match.threshold,
        window_seconds=req.match.window_seconds
    )

    rule = Rule(
        name=req.name,
        type=RuleType(req.type),
        enabled=req.enabled,
        severity=Severity(req.severity),
        description=req.description,
    )

    rule.match = match
    db.add(rule)
    db.flush()
    db.refresh(rule)
    return rule


@router.put("/{id}")
def update(id: int,
           req: create_rule_request,
           db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    '''
    Update an existing rule
    '''
    rule = db.get(Rule, id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.name = req.name
    rule.type = req.type
    rule.enabled = req.enabled
    rule.severity = req.severity
    rule.description = req.description

    rule.match.src_ip = req.match.src_ip
    rule.match.dst_ip = req.match.dst_ip
    rule.match.dst_port = req.match.dst_port
    rule.match.protocol = Protocol(req.match.protocol)
    rule.match.threshold = req.match.threshold
    rule.match.window_seconds = req.match.window_seconds

    db.commit()
    db.refresh(rule)

    return rule


@router.delete("/{id}")
def delete(id: int,
           db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    '''
    Delete a rule
    '''
    rule = db.get(Rule, id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}
