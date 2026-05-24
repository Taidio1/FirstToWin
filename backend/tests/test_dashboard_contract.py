"""Verifies that GET /api/dashboard/stats response matches the frontend DashboardStats type."""
from datetime import datetime, timezone

from app.db.entities.alert import Alert


def test_dashboard_stats_contract(auth_client):
    client, _ = auth_client
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()

    for key in [
        "alerts_24h", "alerts_open", "alerts_critical_open",
        "sensors_online", "sensors_total", "packets_24h",
        "by_severity", "alerts_timeline", "top_sources",
    ]:
        assert key in data, f"Missing key: {key}"

    for key in ["alerts_24h", "alerts_open", "alerts_critical_open",
                "sensors_online", "sensors_total", "packets_24h"]:
        assert isinstance(data[key], int), f"{key} should be int"

    assert isinstance(data["by_severity"], list)
    for item in data["by_severity"]:
        assert "severity" in item and "count" in item
        assert item["severity"] in ("critical", "high", "medium", "low", "info")
        assert isinstance(item["count"], int)

    assert isinstance(data["alerts_timeline"], list)
    assert len(data["alerts_timeline"]) == 24
    for item in data["alerts_timeline"]:
        assert "hour" in item and "count" in item
        assert isinstance(item["count"], int)

    assert isinstance(data["top_sources"], list)
    for item in data["top_sources"]:
        assert "ip" in item and "count" in item and "severity" in item


def test_dashboard_stats_counts_open_critical(auth_client):
    client, Session = auth_client
    with Session() as db:
        alert = Alert(
            rule_id=1, rule_name="Test", severity="critical",
            status="open", src_ip="1.2.3.4", dst_ip="10.0.0.1",
            protocol="TCP", sensor_id="s1", details="test",
            fingerprint="abc123", count=1, last_seen=None,
        )
        db.add(alert)
        db.commit()

    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["alerts_24h"] >= 1
    assert data["alerts_open"] >= 1
    assert data["alerts_critical_open"] >= 1
