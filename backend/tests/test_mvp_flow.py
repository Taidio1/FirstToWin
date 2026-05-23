import os
from datetime import datetime, timedelta, timezone

os.environ["SERVER_HOST"] = "127.0.0.1"
os.environ["SERVER_PORT"] = "8000"
os.environ["DB_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["DEBUG"] = "true"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.db import Base, get_db
from app.db.entities import Alert, NetworkLog, Sensor, User
from app.main import app
from app.middleware.auth import get_current_user
from app.shared_models import AlertStatus, Protocol, SensorStatus, Severity


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_db():
    db = TestingSessionLocal()
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


app.dependency_overrides[get_db] = override_db
app.dependency_overrides[get_current_user] = override_user
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_alerts_are_paginated_and_patch_returns_updated_alert():
    db = TestingSessionLocal()
    alert = Alert(
        rule_id=1,
        rule_name="Port Scan",
        severity=Severity.high.value,
        status=AlertStatus.open.value,
        src_ip="10.10.10.10",
        dst_ip="192.168.1.10",
        protocol=Protocol.TCP.value,
        sensor_id="local-demo-sensor",
        details="Port scan threshold exceeded",
    )
    second_alert = Alert(
        rule_id=2,
        rule_name="Blacklist IP",
        severity=Severity.critical.value,
        status=AlertStatus.open.value,
        src_ip="203.0.113.66",
        dst_ip="192.168.1.10",
        protocol=Protocol.TCP.value,
        sensor_id="local-demo-sensor",
        details="Blacklisted demo IP",
    )
    db.add_all([alert, second_alert])
    db.commit()
    db.close()

    response = client.get("/api/alerts", params={"page": 1, "page_size": 10})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert {item["rule_name"] for item in body["items"]} == {"Port Scan", "Blacklist IP"}

    patch = client.patch(f"/api/alerts/{body['items'][0]['id']}", json={"status": "acknowledged"})

    assert patch.status_code == 200
    assert patch.json()["status"] == "acknowledged"


def test_dashboard_stats_match_frontend_contract():
    db = TestingSessionLocal()
    db.add(Sensor(name="local-demo-sensor", location="local", status=SensorStatus.online))
    db.add(
        Alert(
            rule_id=1,
            rule_name="SSH Brute Force",
            severity=Severity.critical.value,
            status=AlertStatus.open.value,
            src_ip="10.10.10.20",
            dst_ip="192.168.1.20",
            protocol=Protocol.TCP.value,
            sensor_id="local-demo-sensor",
            details="Multiple SSH attempts",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
    )
    db.add(
        NetworkLog(
            sensor_id=1,
            src_ip="10.10.10.20",
            dst_ip="192.168.1.20",
            src_port="51000",
            dst_port="22",
            protocol=Protocol.TCP,
            flags="S",
            payload_size=64,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=3),
        )
    )
    db.commit()
    db.close()

    response = client.get("/api/dashboard/stats")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "alerts_24h",
        "alerts_open",
        "alerts_critical_open",
        "sensors_online",
        "sensors_total",
        "packets_24h",
        "by_severity",
        "alerts_timeline",
        "top_sources",
    }
    assert body["alerts_24h"] == 1
    assert body["alerts_open"] == 1
    assert body["alerts_critical_open"] == 1
    assert body["sensors_online"] == 1
    assert body["sensors_total"] == 1
    assert body["packets_24h"] == 1


def test_ingest_stores_logs_and_creates_port_scan_alert():
    for port in [22, 80, 443, 8080, 8443]:
        response = client.post(
            "/api/ingest/logs",
            json={
                "sensor_name": "local-demo-sensor",
                "src_ip": "10.10.10.30",
                "dst_ip": "192.168.1.30",
                "src_port": 52000 + port,
                "dst_port": port,
                "protocol": "TCP",
                "flags": "S",
                "payload_size": 64,
            },
        )
        assert response.status_code == 201

    body = response.json()
    assert body["log"]["src_ip"] == "10.10.10.30"
    assert any(alert["rule_name"] == "Port Scan" for alert in body["alerts"])

    alerts = client.get("/api/alerts", params={"page": 1, "page_size": 10}).json()
    logs = client.get("/api/logs", params={"page": 1, "page_size": 10}).json()
    assert alerts["total"] >= 1
    assert logs["total"] == 5
