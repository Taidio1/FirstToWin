from app.models.auth_model import login_request, register_request
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.entities import User
from sqlalchemy import select
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
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register(req: register_request,
             db: Session = Depends(get_db)):
    '''
    Registers a user
    '''
    user = User(email=req.email, username=req.username,
                password=hash_password(req.password), role="viewer")

    db.add(user)
    db.commit()
    return user
