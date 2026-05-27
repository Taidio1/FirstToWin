from app.db.entities import User
from app.helpers.login_helper import hash_password


def test_user_cannot_create_rule(plain_client):
    client, Session = plain_client
    db = Session()
    db.add(
        User(
            email="user@example.local",
            username="regular",
            password=hash_password("pass"),
            role="user",
        )
    )
    db.commit()
    db.close()

    login = client.post(
        "/api/auth/login",
        json={"email": "user@example.local", "password": "pass"},
    )
    token = login.json()["access_token"]

    r = client.post(
        "/api/rules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Blocked by role",
            "type": "port_scan",
            "enabled": True,
            "severity": "high",
            "description": "Only admins may create rules.",
            "match": {
                "protocol": "TCP",
                "threshold": 5,
                "window_seconds": 60,
            },
        },
    )

    assert r.status_code == 403


def test_admin_can_create_rule(plain_client):
    client, Session = plain_client
    db = Session()
    db.add(
        User(
            email="admin@example.local",
            username="admin",
            password=hash_password("pass"),
            role="admin",
        )
    )
    db.commit()
    db.close()

    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.local", "password": "pass"},
    )
    token = login.json()["access_token"]

    r = client.post(
        "/api/rules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Allowed by role",
            "type": "port_scan",
            "enabled": True,
            "severity": "high",
            "description": "Admins may create rules.",
            "match": {
                "protocol": "TCP",
                "threshold": 5,
                "window_seconds": 60,
            },
        },
    )

    assert r.status_code == 200
    assert r.json()["name"] == "Allowed by role"
