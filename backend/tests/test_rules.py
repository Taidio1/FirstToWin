from app.db.entities import Sensor

PORT_SCAN_RULE = {
    "name": "Test Port Scan",
    "type": "port_scan",
    "enabled": True,
    "severity": "high",
    "match": {"protocol": "TCP", "threshold": 5, "window_seconds": 60},
    "description": "Detects rapid port scanning activity.",
}

BLACKLIST_RULE = {
    "name": "Test Blacklist",
    "type": "blacklist_ip",
    "enabled": True,
    "severity": "critical",
    "match": {"src_ip": "10.0.0.99", "protocol": "TCP"},
    "description": "Blocks a known bad actor IP.",
}


def test_create_rule_returns_rule_with_id(auth_client):
    client, _ = auth_client

    r = client.post("/api/rules", json=PORT_SCAN_RULE)

    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Test Port Scan"
    assert body["type"] == "port_scan"
    assert body["severity"] == "high"
    assert body["enabled"] is True
    assert "id" in body
    assert body["hit_count"] == 0


def test_list_rules_returns_all_created_rules(auth_client):
    client, _ = auth_client
    client.post("/api/rules", json=PORT_SCAN_RULE)
    client.post("/api/rules", json=BLACKLIST_RULE)

    r = client.get("/api/rules")

    assert r.status_code == 200
    names = {rule["name"] for rule in r.json()}
    assert "Test Port Scan" in names
    assert "Test Blacklist" in names


def test_update_rule_changes_name_and_enabled(auth_client):
    client, _ = auth_client
    create = client.post("/api/rules", json=PORT_SCAN_RULE)
    rule_id = create.json()["id"]

    updated = {**PORT_SCAN_RULE, "name": "Updated Port Scan", "enabled": False}
    r = client.put(f"/api/rules/{rule_id}", json=updated)

    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Updated Port Scan"
    assert body["enabled"] is False


def test_delete_rule_removes_it(auth_client):
    client, _ = auth_client
    create = client.post("/api/rules", json=BLACKLIST_RULE)
    rule_id = create.json()["id"]

    r = client.delete(f"/api/rules/{rule_id}")
    assert r.status_code in (200, 204)

    rules = client.get("/api/rules").json()
    assert all(rule["id"] != rule_id for rule in rules)


def test_delete_nonexistent_rule_returns_404(auth_client):
    client, _ = auth_client

    r = client.delete("/api/rules/99999")

    assert r.status_code == 404


def test_disabled_rule_does_not_trigger_alert_on_ingest(auth_client):
    client, Session = auth_client
    db = Session()
    db.add(Sensor(name="local-demo-sensor", location="local", status="online", api_key="demo-sensor-key"))
    db.commit()
    db.close()

    client.post("/api/rules", json={**PORT_SCAN_RULE, "enabled": False})

    for port in [22, 80, 443, 8080, 8443]:
        client.post(
            "/api/ingest/logs",
            headers={"X-Sensor-Key": "demo-sensor-key"},
            json={
                "sensor_name": "local-demo-sensor",
                "src_ip": "10.10.10.50",
                "dst_ip": "192.168.1.50",
                "src_port": 60000 + port,
                "dst_port": port,
                "protocol": "TCP",
                "flags": "S",
                "payload_size": 64,
            },
        )

    alerts = client.get("/api/alerts", params={"page": 1, "page_size": 10}).json()
    port_scan_alerts = [
        a for a in alerts["items"]
        if a["rule_name"] == "Test Port Scan" and a["src_ip"] == "10.10.10.50"
    ]
    assert len(port_scan_alerts) == 0
