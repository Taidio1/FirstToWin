from app.db.entities import User
from app.helpers.login_helper import hash_password
import app.settings as settings
import importlib

auth_router = importlib.import_module("app.routers.auth_router")
auth_middleware = importlib.import_module("app.middleware.auth")


def test_login_returns_token_for_valid_credentials(plain_client):
    client, Session = plain_client
    db = Session()
    db.add(User(email="u@example.local", username="u", password=hash_password("pass"), role="admin"))
    db.commit()
    db.close()

    r = client.post("/api/auth/login", json={"email": "u@example.local", "password": "pass"})

    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "u@example.local"


def test_login_rejects_wrong_password(plain_client):
    client, Session = plain_client
    db = Session()
    db.add(User(email="u2@example.local", username="u2", password=hash_password("correct"), role="admin"))
    db.commit()
    db.close()

    r = client.post("/api/auth/login", json={"email": "u2@example.local", "password": "wrong"})

    assert r.status_code == 401


def test_login_rejects_unknown_email(plain_client):
    client, _ = plain_client

    r = client.post("/api/auth/login", json={"email": "nobody@example.local", "password": "pass"})

    assert r.status_code == 401


def test_register_creates_new_user(plain_client):
    client, _ = plain_client

    r = client.post("/api/auth/register", json={
        "email": "new@example.local",
        "username": "newuser",
        "password": "newpass123",
    })

    assert r.status_code in (200, 201)
    assert r.json()["email"] == "new@example.local"


def test_login_uses_supabase_auth_when_configured(monkeypatch, plain_client):
    client, _ = plain_client

    class FakeSupabaseAuth:
        def sign_in_with_password(self, email, password):
            assert email == "supa@example.local"
            assert password == "pass1234"
            return {
                "access_token": "supabase-access-token",
                "user": {
                    "id": "2db44ac6-4fc8-4b58-bb70-8bdf9e662abb",
                    "email": email,
                    "user_metadata": {"username": "supa"},
                },
            }

    monkeypatch.setattr(settings, "SUPABASE_URL", "https://project.supabase.co", raising=False)
    monkeypatch.setattr(settings, "SUPABASE_ANON_KEY", "anon-key", raising=False)
    monkeypatch.setattr(auth_router, "get_supabase_auth_client", lambda: FakeSupabaseAuth(), raising=False)

    r = client.post("/api/auth/login", json={"email": "supa@example.local", "password": "pass1234"})

    assert r.status_code == 200
    body = r.json()
    assert body["access_token"] == "supabase-access-token"
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "supa@example.local"
    assert body["user"]["username"] == "supa"
    assert body["user"]["role"] == "user"


def test_register_uses_supabase_auth_and_stores_profile(monkeypatch, plain_client):
    client, Session = plain_client

    class FakeSupabaseAuth:
        def sign_up(self, email, password, username):
            assert email == "new-supa@example.local"
            assert password == "pass1234"
            assert username == "new-supa"
            return {
                "user": {
                    "id": "f4127528-640b-48d0-b369-7a95e9b6e1b9",
                    "email": email,
                    "user_metadata": {"username": username},
                }
            }

    monkeypatch.setattr(settings, "SUPABASE_URL", "https://project.supabase.co", raising=False)
    monkeypatch.setattr(settings, "SUPABASE_ANON_KEY", "anon-key", raising=False)
    monkeypatch.setattr(auth_router, "get_supabase_auth_client", lambda: FakeSupabaseAuth(), raising=False)

    r = client.post("/api/auth/register", json={
        "email": "new-supa@example.local",
        "username": "new-supa",
        "password": "pass1234",
    })

    assert r.status_code in (200, 201)
    body = r.json()
    assert body["email"] == "new-supa@example.local"
    assert body["role"] == "user"

    db = Session()
    user = db.query(User).filter(User.email == "new-supa@example.local").one()
    db.close()
    assert user.supabase_user_id == "f4127528-640b-48d0-b369-7a95e9b6e1b9"
    assert user.password is None


def test_supabase_bearer_token_creates_profile(monkeypatch, plain_client):
    client, Session = plain_client

    class FakeSupabaseAuth:
        def get_user(self, token):
            assert token == "valid-supabase-token"
            return {
                "id": "ad5290b0-6200-42ef-a66d-a63c5783f771",
                "email": "token@example.local",
                "user_metadata": {"username": "token-user"},
            }

    monkeypatch.setattr(settings, "SUPABASE_URL", "https://project.supabase.co", raising=False)
    monkeypatch.setattr(settings, "SUPABASE_ANON_KEY", "anon-key", raising=False)
    monkeypatch.setattr(auth_middleware, "get_supabase_auth_client", lambda: FakeSupabaseAuth(), raising=False)

    r = client.get("/api/alerts", headers={"Authorization": "Bearer valid-supabase-token"})

    assert r.status_code == 200
    db = Session()
    user = db.query(User).filter(User.email == "token@example.local").one()
    db.close()
    assert user.supabase_user_id == "ad5290b0-6200-42ef-a66d-a63c5783f771"
    assert user.role == "user"


def test_register_rejects_duplicate_email(plain_client):
    client, _ = plain_client

    client.post("/api/auth/register", json={"email": "dup@example.local", "username": "dup1", "password": "p1"})
    r = client.post("/api/auth/register", json={"email": "dup@example.local", "username": "dup2", "password": "p2"})

    assert r.status_code in (400, 409, 422)


def test_protected_endpoint_requires_token(plain_client):
    client, _ = plain_client

    r = client.get("/api/alerts")

    assert r.status_code == 401
