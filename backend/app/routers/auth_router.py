from app.models.auth_model import login_request, register_request
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from app.db.db import get_db
from app.db.entities import User
from app.helpers.login_helper import verify_password, hash_password
from app.helpers.jwt_helper import create_access_token
router = APIRouter()


@router.post("/login")
def login(req: login_request,
          db: Session = Depends(get_db)):
    '''
    Login the user
    returns:
    - 401 if invalid credentials
    - access_token otherwise
    '''
    query = select(User).where(
        User.email == req.email)
    user = db.scalars(query).one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(req.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({
        "sub": str(user.id)
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at
        }
    }


@router.post("/register")
def register(req: register_request,
             db: Session = Depends(get_db)):
    '''
    Registers a user
    '''
    query = select(User).where(
        or_(User.email == req.email, User.username == req.username)
    )
    user = db.scalars(query).one_or_none()

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    user = User(email=req.email, username=req.username,
                password=hash_password(req.password), role="viewer")
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    return user
