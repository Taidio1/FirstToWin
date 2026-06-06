def test_create_sensor_returns_201_with_api_key(auth_client):
    client, _ = auth_client

    r = client.post("/api/sensors", json={"name": "sensor-x", "location": "rack-1", "status": "online"})

    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "sensor-x"
    assert "api_key" in body
    assert len(body["api_key"]) > 8


def test_list_sensors_returns_created_sensors(auth_client):
    client, _ = auth_client
    client.post("/api/sensors", json={"name": "sensor-a", "location": "floor-1", "status": "online"})
    client.post("/api/sensors", json={"name": "sensor-b", "location": "floor-2", "status": "offline"})

    r = client.get("/api/sensors")

    assert r.status_code == 200
    names = {s["name"] for s in r.json()}
    assert "sensor-a" in names
    assert "sensor-b" in names


def test_delete_sensor_removes_it_from_list(auth_client):
    client, _ = auth_client
    create = client.post("/api/sensors", json={"name": "to-delete", "location": "temp", "status": "online"})
    sensor_id = create.json()["id"]

    delete = client.delete(f"/api/sensors/{sensor_id}")
    assert delete.status_code in (200, 204)

    sensors = client.get("/api/sensors").json()
    assert all(s["id"] != sensor_id for s in sensors)


def test_delete_nonexistent_sensor_returns_404(auth_client):
    client, _ = auth_client

    r = client.delete("/api/sensors/99999")

    assert r.status_code == 404
