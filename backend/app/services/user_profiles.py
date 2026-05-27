from __future__ import annotations

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.db.entities import User


def get_or_create_supabase_profile(db: Session, supabase_user: dict) -> User:
    supabase_user_id = supabase_user["id"]
    email = supabase_user["email"]
    metadata = supabase_user.get("user_metadata") or {}
    username = metadata.get("username") or email.split("@", 1)[0]

    user = db.scalars(
        select(User).where(
            or_(
                User.supabase_user_id == supabase_user_id,
                User.email == email,
            )
        )
    ).one_or_none()

    if user is None:
        user = User(
            supabase_user_id=supabase_user_id,
            email=email,
            username=username,
            role="user",
            password=None,
        )
        db.add(user)
    else:
        user.supabase_user_id = supabase_user_id
        user.email = email
        if not user.username:
            user.username = username
        if user.role not in ("admin", "user"):
            user.role = "user"

    db.commit()
    db.refresh(user)
    return user
