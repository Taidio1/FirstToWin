from app.services.demo_seed import DEMO_BLACKLIST_IP


def _blacklist_payload(src_port: int = 54000) -> dict:
    return {
        "sensor_name": "local-demo-sensor",
        "src_ip": DEMO_BLACKLIST_IP,
        "dst_ip": "192.168.56.42",
        "src_port": src_port,
        "dst_port": 443,
        "protocol": "TCP",
        "flags": "S",
        "payload_size": 128,
    }


def test_alert_websocket_accepts_connections(auth_client):
    client, _ = auth_client

    with client.websocket_connect("/api/alerts/ws") as websocket:
        message = websocket.receive_json()

    assert message == {"type": "alerts.connected"}


def test_ingest_publishes_new_alert_to_websocket(auth_client):
    client, _ = auth_client

    with client.websocket_connect("/api/alerts/ws") as websocket:
        assert websocket.receive_json() == {"type": "alerts.connected"}

        response = client.post(
            "/api/ingest/logs",
            headers={"X-Sensor-Key": "demo-sensor-key"},
            json=_blacklist_payload(),
        )
        message = websocket.receive_json()

    assert response.status_code == 201
    assert message["type"] == "alert.created"
    assert message["alert"]["rule_name"] == "Blacklist IP"
    assert message["alert"]["src_ip"] == DEMO_BLACKLIST_IP
    assert message["alert"]["count"] == 1


def test_ingest_publishes_duplicate_alert_as_update(auth_client):
    client, _ = auth_client

    first = client.post(
        "/api/ingest/logs",
        headers={"X-Sensor-Key": "demo-sensor-key"},
        json=_blacklist_payload(54001),
    )
    assert first.status_code == 201

    with client.websocket_connect("/api/alerts/ws") as websocket:
        assert websocket.receive_json() == {"type": "alerts.connected"}

        response = client.post(
            "/api/ingest/logs",
            headers={"X-Sensor-Key": "demo-sensor-key"},
            json=_blacklist_payload(54002),
        )
        message = websocket.receive_json()

    assert response.status_code == 201
    assert message["type"] == "alert.updated"
    assert message["alert"]["rule_name"] == "Blacklist IP"
    assert message["alert"]["count"] == 2
    assert message["alert"]["last_seen"] is not None
