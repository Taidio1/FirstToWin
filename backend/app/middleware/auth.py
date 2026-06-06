from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.helpers.jwt_helper import verify_token
from app.db.entities import User
from app.services.supabase_auth import (
    SupabaseAuthError,
    get_supabase_auth_client,
    is_supabase_auth_enabled,
)
from app.services.user_profiles import get_or_create_supabase_profile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if is_supabase_auth_enabled():
        try:
            supabase_user = get_supabase_auth_client().get_user(token)
        except SupabaseAuthError as exc:
            raise HTTPException(401, "Invalid token") from exc
        return get_or_create_supabase_profile(db, supabase_user)

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


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin role required")
    return user
