from app.db.entities import User
from app.helpers.login_helper import hash_password


def test_login_returns_token_for_valid_credentials(plain_client):
    client, Session = plain_client
    db = Session()
    db.add(User(email="u@example.local", username="u", password=hash_password("pass"), role="analyst"))
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
    db.add(User(email="u2@example.local", username="u2", password=hash_password("correct"), role="analyst"))
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


def test_register_rejects_duplicate_email(plain_client):
    client, _ = plain_client

    client.post("/api/auth/register", json={"email": "dup@example.local", "username": "dup1", "password": "p1"})
    r = client.post("/api/auth/register", json={"email": "dup@example.local", "username": "dup2", "password": "p2"})

    assert r.status_code in (400, 409, 422)


def test_protected_endpoint_requires_token(plain_client):
    client, _ = plain_client

    r = client.get("/api/alerts")

    assert r.status_code == 401
