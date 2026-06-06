from __future__ import annotations

import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulate_attack import BLACKLIST_IP, DEFAULT_SENSOR_KEY, build_payloads, post_json

DEFAULT_BACKEND_URL = "http://backend:8000"
DEFAULT_THREAT_TYPES = ("port-scan", "ssh-bruteforce", "blacklist")
INGEST_PATH = "/api/ingest/logs"
HEALTH_PATH = "/api/health"


@dataclass(frozen=True)
class LiveSimulatorConfig:
    backend_url: str
    sensor_key: str
    normal_interval_seconds: int
    threat_interval_seconds: int
    threat_types: tuple[str, ...]


@dataclass(frozen=True)
class SendResult:
    sent: int
    alerts: int


def load_config() -> LiveSimulatorConfig:
    return LiveSimulatorConfig(
        backend_url=os.environ.get("LIVE_BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/"),
        sensor_key=os.environ.get("LIVE_SENSOR_KEY", DEFAULT_SENSOR_KEY),
        normal_interval_seconds=int(os.environ.get("LIVE_NORMAL_INTERVAL_SECONDS", "5")),
        threat_interval_seconds=int(os.environ.get("LIVE_THREAT_INTERVAL_SECONDS", "30")),
        threat_types=parse_threat_types(
            os.environ.get("LIVE_THREAT_TYPES", ",".join(DEFAULT_THREAT_TYPES))
        ),
    )


def parse_threat_types(raw: str) -> tuple[str, ...]:
    threat_types = tuple(item.strip() for item in raw.split(",") if item.strip())
    invalid = sorted(set(threat_types) - set(DEFAULT_THREAT_TYPES))
    if invalid:
        raise ValueError(f"Unsupported LIVE_THREAT_TYPES values: {', '.join(invalid)}")
    return threat_types or DEFAULT_THREAT_TYPES


def build_live_payloads(traffic_type: str, sequence: int = 0) -> list[dict]:
    payloads = build_payloads(traffic_type)
    dst_host = 10 + (sequence % 200)
    src_host = 20 + (sequence % 200)

    live_payloads = []
    for payload in payloads:
        next_payload = payload | {
            "sensor_name": "local-demo-sensor",
            "dst_ip": f"192.168.56.{dst_host}",
        }
        if traffic_type == "port-scan":
            next_payload["src_ip"] = f"10.10.30.{src_host}"
        elif traffic_type == "ssh-bruteforce":
            next_payload["src_ip"] = f"10.10.40.{src_host}"
        live_payloads.append(next_payload)
    return live_payloads


def send_payloads(backend_url: str, sensor_key: str, payloads: list[dict]) -> SendResult:
    alerts = 0
    sent = 0
    ingest_url = f"{backend_url.rstrip('/')}{INGEST_PATH}"
    for payload in payloads:
        try:
            response = post_json(ingest_url, payload, sensor_key)
        except SystemExit as exc:
            print(f"[live-simulator] ingest failed error={exc}", flush=True)
            continue
        sent += 1
        alerts += len(response.get("alerts", []))
        time.sleep(0.05)
    return SendResult(sent=sent, alerts=alerts)


def wait_for_backend(backend_url: str, retry_seconds: int = 2) -> None:
    health_url = f"{backend_url.rstrip('/')}{HEALTH_PATH}"
    while True:
        try:
            request = Request(health_url, method="GET")
            with urlopen(request, timeout=5) as response:
                if 200 <= response.status < 300:
                    print(f"[live-simulator] backend healthy url={health_url}", flush=True)
                    return
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"[live-simulator] waiting for backend url={health_url} error={exc}", flush=True)
        time.sleep(retry_seconds)


def run(config: LiveSimulatorConfig) -> None:
    if not config.threat_types:
        raise SystemExit("LIVE_THREAT_TYPES must contain at least one supported threat type.")

    wait_for_backend(config.backend_url)
    sequence = 0
    next_threat_at = time.monotonic() + config.threat_interval_seconds

    while True:
        sequence += 1
        normal = send_payloads(
            config.backend_url,
            config.sensor_key,
            build_live_payloads("normal", sequence),
        )
        print(
            f"[live-simulator] normal sent={normal.sent} alerts={normal.alerts}",
            flush=True,
        )

        now = time.monotonic()
        if now >= next_threat_at:
            threat_type = random.choice(config.threat_types)
            threat = send_payloads(
                config.backend_url,
                config.sensor_key,
                build_live_payloads(threat_type, sequence),
            )
            print(
                f"[live-simulator] threat={threat_type} sent={threat.sent} alerts={threat.alerts}",
                flush=True,
            )
            next_threat_at = now + config.threat_interval_seconds

        time.sleep(config.normal_interval_seconds)


def main() -> int:
    try:
        run(load_config())
    except KeyboardInterrupt:
        print("[live-simulator] stopped", flush=True)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
