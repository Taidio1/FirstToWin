import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_script(script_name: str):
    script_path = REPO_ROOT / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.removesuffix(".py"), script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_simulator_full_demo_combines_normal_and_attack_traffic():
    simulator = load_script("simulate_attack.py")

    payloads = simulator.build_payloads("full-demo")

    assert len(payloads) > len(simulator.build_payloads("port-scan"))
    assert any(payload["src_ip"] == simulator.BLACKLIST_IP for payload in payloads)
    assert any(payload["dst_port"] == 22 for payload in payloads)
    assert any(payload["flags"] == "A" for payload in payloads)


def test_simulator_sends_sensor_key_header(monkeypatch):
    simulator = load_script("simulate_attack.py")
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'{"alerts": []}'

    def fake_urlopen(request, timeout):
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(simulator, "urlopen", fake_urlopen)

    simulator.post_json(
        "http://localhost:8000/api/ingest/logs",
        simulator.build_payloads("blacklist")[0],
        "demo-sensor-key",
    )

    assert captured["headers"]["X-sensor-key"] == "demo-sensor-key"
    assert captured["timeout"] == 10


def test_smoke_demo_script_exposes_main_entrypoint():
    smoke_demo = load_script("smoke_demo.py")

    assert callable(smoke_demo.main)


def test_smoke_demo_can_override_port_scan_source_ip():
    smoke_demo = load_script("smoke_demo.py")

    payloads = smoke_demo.build_smoke_payloads("10.250.1.42")

    assert len(payloads) == 5
    assert {payload["src_ip"] for payload in payloads} == {"10.250.1.42"}
