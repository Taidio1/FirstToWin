from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.helpers.jwt_helper import verify_token
from app.db.entities import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(401, "Invalid token")

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(401, "Invalid token")

    stmt = select(User).where(User.id == int(user_id))

    user = db.scalars(stmt).one_or_none()

    if user is None:
        raise HTTPException(401, "User not found")

    return user
