"""
Shared pytest fixtures for tests that need an isolated in-memory DB.
test_mvp_flow.py manages its own overrides at module level and is left untouched.
"""
import os

os.environ.setdefault("SERVER_HOST", "127.0.0.1")
os.environ.setdefault("SERVER_PORT", "8000")
os.environ.setdefault("DB_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("DEBUG", "true")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.db import Base, get_db
from app.db.entities import User
from app.main import app
from app.middleware.auth import get_current_user


def _make_engine():
    return create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture()
def db_engine():
    engine = _make_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def plain_client(db_engine):
    Session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    prev_db = app.dependency_overrides.get(get_db)
    prev_user = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_user, None)

    yield TestClient(app), Session

    if prev_db is not None:
        app.dependency_overrides[get_db] = prev_db
    else:
        app.dependency_overrides.pop(get_db, None)

    if prev_user is not None:
        app.dependency_overrides[get_current_user] = prev_user
    else:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def auth_client(db_engine):
    Session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    def override_user():
        return User(
            id=1,
            email="demo@example.local",
            username="demo",
            role="analyst",
            password="unused",
        )

    prev_db = app.dependency_overrides.get(get_db)
    prev_user = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    yield TestClient(app), Session

    if prev_db is not None:
        app.dependency_overrides[get_db] = prev_db
    else:
        app.dependency_overrides.pop(get_db, None)

    if prev_user is not None:
        app.dependency_overrides[get_current_user] = prev_user
    else:
        app.dependency_overrides.pop(get_current_user, None)
