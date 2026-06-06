from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "http://localhost:8000/api/ingest/logs"
BLACKLIST_IP = "203.0.113.66"
DEFAULT_SENSOR_KEY = "demo-sensor-key"


def main() -> int:
    parser = argparse.ArgumentParser(description="Send local demo attack logs to the NDR backend.")
    parser.add_argument(
        "--type",
        choices=("normal", "port-scan", "ssh-bruteforce", "blacklist", "full-demo"),
        required=True,
        help="Demo traffic pattern to generate.",
    )
    parser.add_argument("--url", default=API_URL, help="Local ingest endpoint URL.")
    parser.add_argument(
        "--sensor-key",
        default=os.environ.get("NDR_SENSOR_KEY", DEFAULT_SENSOR_KEY),
        help="Sensor API key sent in the X-Sensor-Key header.",
    )
    args = parser.parse_args()

    alerts = []
    for payload in build_payloads(args.type):
        response = post_json(args.url, payload, args.sensor_key)
        alerts.extend(response.get("alerts", []))
        time.sleep(0.05)

    print(f"sent={len(build_payloads(args.type))} alerts={len(alerts)}")
    for alert in alerts:
        print(
            f"alert id={alert['id']} rule={alert['rule_name']} "
            f"severity={alert['severity']} src={alert['src_ip']} dst={alert['dst_ip']}"
        )
    return 0


def build_payloads(attack_type: str) -> list[dict]:
    base = {
        "sensor_name": "local-demo-sensor",
        "dst_ip": "192.168.56.10",
        "protocol": "TCP",
        "flags": "S",
        "payload_size": 64,
    }

    if attack_type == "normal":
        return [
            base | {
                "src_ip": "10.10.10.10",
                "src_port": 50000 + i,
                "dst_port": port,
                "flags": "A",
                "payload_size": 256,
            }
            for i, port in enumerate([80, 443, 443], start=1)
        ]

    if attack_type == "port-scan":
        return [
            base | {
                "src_ip": "10.10.10.30",
                "src_port": 52000 + i,
                "dst_port": port,
            }
            for i, port in enumerate([22, 80, 443, 8080, 8443], start=1)
        ]

    if attack_type == "ssh-bruteforce":
        return [
            base | {
                "src_ip": "10.10.10.40",
                "src_port": 53000 + i,
                "dst_port": 22,
            }
            for i in range(1, 6)
        ]

    if attack_type == "blacklist":
        return [
            base | {
                "src_ip": BLACKLIST_IP,
                "src_port": 54001,
                "dst_port": 443,
            }
        ]

    payloads = []
    for demo_type in ("normal", "port-scan", "ssh-bruteforce", "blacklist"):
        payloads.extend(build_payloads(demo_type))
    return payloads


def post_json(url: str, payload: dict, sensor_key: str) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Sensor-Key": sensor_key,
        },
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
