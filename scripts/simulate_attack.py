from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "http://localhost:8000/api/ingest/logs"
BLACKLIST_IP = "203.0.113.66"


def main() -> int:
    parser = argparse.ArgumentParser(description="Send local demo attack logs to the NDR backend.")
    parser.add_argument(
        "--type",
        choices=("port-scan", "ssh-bruteforce", "blacklist"),
        required=True,
        help="Demo traffic pattern to generate.",
    )
    parser.add_argument("--url", default=API_URL, help="Local ingest endpoint URL.")
    args = parser.parse_args()

    alerts = []
    for payload in build_payloads(args.type):
        response = post_json(args.url, payload)
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

    return [
        base | {
            "src_ip": BLACKLIST_IP,
            "src_port": 54001,
            "dst_port": 443,
        }
    ]


def post_json(url: str, payload: dict) -> dict:
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
