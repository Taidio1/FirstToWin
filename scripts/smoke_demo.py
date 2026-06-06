from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulate_attack import DEFAULT_SENSOR_KEY, build_payloads, post_json

BASE_URL = "http://localhost:8000"
DEMO_EMAIL = "demo@example.local"
DEMO_PASSWORD = "demo1234"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a quick end-to-end NDR demo smoke test.")
    parser.add_argument("--base-url", default=BASE_URL, help="Backend base URL.")
    parser.add_argument("--email", default=DEMO_EMAIL, help="Demo user email.")
    parser.add_argument("--password", default=DEMO_PASSWORD, help="Demo user password.")
    parser.add_argument("--sensor-key", default=DEFAULT_SENSOR_KEY, help="Demo sensor API key.")
    parser.add_argument(
        "--src-ip",
        default=f"10.250.{int(time.time()) % 250}.{(int(time.time()) // 250) % 250}",
        help="Source IP used by the smoke-test port scan.",
    )
    args = parser.parse_args()

    health = get_json(f"{args.base_url}/api/health")
    if health.get("status") != "ok" or health.get("database") != "ok":
        raise SystemExit(f"Healthcheck failed: {health}")

    token = login(args.base_url, args.email, args.password)
    before = get_json(f"{args.base_url}/api/dashboard/stats", token)

    ingest_url = f"{args.base_url}/api/ingest/logs"
    for payload in build_smoke_payloads(args.src_ip):
        post_json(ingest_url, payload, args.sensor_key)

    after = get_json(f"{args.base_url}/api/dashboard/stats", token)
    if after["alerts_24h"] <= before["alerts_24h"]:
        raise SystemExit(
            f"Expected alerts_24h to increase, before={before['alerts_24h']} after={after['alerts_24h']}"
        )

    print(
        "smoke=ok "
        f"alerts_24h_before={before['alerts_24h']} "
        f"alerts_24h_after={after['alerts_24h']} "
        f"packets_24h_after={after['packets_24h']}"
    )
    return 0


def build_smoke_payloads(src_ip: str) -> list[dict]:
    return [payload | {"src_ip": src_ip} for payload in build_payloads("port-scan")]


def login(base_url: str, email: str, password: str) -> str:
    body = post_json_without_sensor_key(
        f"{base_url}/api/auth/login",
        {"email": email, "password": password},
    )
    return body["access_token"]


def get_json(url: str, token: str | None = None) -> dict:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach {url}: {exc.reason}") from exc


def post_json_without_sensor_key(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach {url}: {exc.reason}") from exc


if __name__ == "__main__":
    sys.exit(main())
