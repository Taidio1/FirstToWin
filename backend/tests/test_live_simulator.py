import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_live_simulator():
    script_path = REPO_ROOT / "scripts" / "live_simulator.py"
    spec = importlib.util.spec_from_file_location("live_simulator", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_load_config_uses_demo_defaults(monkeypatch):
    simulator = load_live_simulator()
    for name in (
        "LIVE_BACKEND_URL",
        "LIVE_SENSOR_KEY",
        "LIVE_NORMAL_INTERVAL_SECONDS",
        "LIVE_THREAT_INTERVAL_SECONDS",
        "LIVE_THREAT_TYPES",
    ):
        monkeypatch.delenv(name, raising=False)

    config = simulator.load_config()

    assert config.backend_url == "http://backend:8000"
    assert config.sensor_key == "demo-sensor-key"
    assert config.normal_interval_seconds == 5
    assert config.threat_interval_seconds == 30
    assert config.threat_types == ("port-scan", "ssh-bruteforce", "blacklist")


def test_parse_threat_types_trims_empty_items():
    simulator = load_live_simulator()

    threat_types = simulator.parse_threat_types(" port-scan, ,blacklist,ssh-bruteforce ")

    assert threat_types == ("port-scan", "blacklist", "ssh-bruteforce")


def test_build_live_payloads_marks_normal_and_threat_traffic():
    simulator = load_live_simulator()

    normal = simulator.build_live_payloads("normal")
    port_scan = simulator.build_live_payloads("port-scan")
    blacklist = simulator.build_live_payloads("blacklist")

    assert len(normal) == 3
    assert all(payload["sensor_name"] == "local-demo-sensor" for payload in normal)
    assert all(payload["flags"] == "A" for payload in normal)
    assert len({payload["dst_port"] for payload in port_scan}) >= 5
    assert blacklist[0]["src_ip"] == simulator.BLACKLIST_IP


def test_send_payloads_posts_to_ingest_endpoint_with_sensor_key(monkeypatch):
    simulator = load_live_simulator()
    captured = []

    def fake_post_json(url, payload, sensor_key):
        captured.append({"url": url, "payload": payload, "sensor_key": sensor_key})
        return {"alerts": [{"id": 1}, {"id": 2}]}

    monkeypatch.setattr(simulator, "post_json", fake_post_json)

    result = simulator.send_payloads(
        "http://backend:8000",
        "demo-sensor-key",
        simulator.build_live_payloads("blacklist"),
    )

    assert result.sent == 1
    assert result.alerts == 2
    assert captured[0]["url"] == "http://backend:8000/api/ingest/logs"
    assert captured[0]["sensor_key"] == "demo-sensor-key"


def test_send_payloads_keeps_simulator_alive_on_transient_post_error(monkeypatch):
    simulator = load_live_simulator()

    def failing_post_json(url, payload, sensor_key):
        raise SystemExit("Could not reach backend")

    monkeypatch.setattr(simulator, "post_json", failing_post_json)

    result = simulator.send_payloads(
        "http://backend:8000",
        "demo-sensor-key",
        simulator.build_live_payloads("blacklist"),
    )

    assert result.sent == 0
    assert result.alerts == 0
