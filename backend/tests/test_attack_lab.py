import pytest
from app.services import attack_lab


@pytest.fixture(autouse=True)
def reset_auto_attack():
    attack_lab.stop_auto()
    yield
    attack_lab.stop_auto()


def test_status_returns_expected_structure(auth_client):
    client, _ = auth_client
    response = client.get("/api/attack-lab/status")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "running",
        "interval_seconds",
        "next_run_at",
        "seconds_remaining",
        "last_scenario",
        "last_result",
    }
    assert body["running"] is False
    assert body["seconds_remaining"] is None


def test_run_rejects_unknown_scenario(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/run", json={"scenario": "hack-the-planet"})
    assert response.status_code == 400


def test_run_rejects_injection_attempts(auth_client):
    client, _ = auth_client
    for bad in ["rm -rf /", "'; DROP TABLE--", "../../etc/passwd", ""]:
        response = client.post("/api/attack-lab/run", json={"scenario": bad})
        assert response.status_code == 400, f"Expected 400 for: {bad!r}"


def test_run_blacklist_scenario(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/run", json={"scenario": "blacklist"})
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "blacklist"
    assert body["payloads_sent"] == 1
    assert body["alerts_created"] >= 0


def test_run_port_scan_scenario(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/run", json={"scenario": "port-scan"})
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "port-scan"
    assert body["payloads_sent"] == 5


def test_run_ssh_bruteforce_scenario(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/run", json={"scenario": "ssh-bruteforce"})
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "ssh-bruteforce"
    assert body["payloads_sent"] == 5


def test_run_full_demo_scenario(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/run", json={"scenario": "full-demo"})
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"] == "full-demo"
    assert body["payloads_sent"] == 14  # 3 + 5 + 5 + 1


def test_auto_start_updates_status(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/auto/start", json={"interval_seconds": 60})
    assert response.status_code == 200
    body = response.json()
    assert body["running"] is True
    assert body["interval_seconds"] == 60
    assert body["seconds_remaining"] is not None
    assert 0 <= body["seconds_remaining"] <= 60


def test_auto_stop_clears_status(auth_client):
    client, _ = auth_client
    client.post("/api/attack-lab/auto/start", json={"interval_seconds": 60})
    response = client.post("/api/attack-lab/auto/stop")
    assert response.status_code == 200
    body = response.json()
    assert body["running"] is False
    assert body["seconds_remaining"] is None


def test_auto_start_rejects_interval_below_minimum(auth_client):
    client, _ = auth_client
    response = client.post("/api/attack-lab/auto/start", json={"interval_seconds": 1})
    assert response.status_code == 422


def test_all_allowed_scenarios_run_without_error(auth_client):
    client, _ = auth_client
    for scenario in attack_lab.ALLOWED_SCENARIOS:
        response = client.post("/api/attack-lab/run", json={"scenario": scenario})
        assert response.status_code == 200, f"Scenario {scenario!r} failed"
