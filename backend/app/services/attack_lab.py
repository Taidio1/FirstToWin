from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.db.db import SessionLocal
from app.db.entities import NetworkLog
from app.services.demo_seed import DEMO_SENSOR_NAME, ensure_demo_data
from app.services.detection_engine import detect_alerts

ALLOWED_SCENARIOS = ["normal", "port-scan", "ssh-bruteforce", "blacklist", "full-demo"]
AUTO_SCENARIOS = ["port-scan", "ssh-bruteforce", "blacklist"]
BLACKLIST_IP = "203.0.113.66"


def build_payloads(attack_type: str) -> list[dict]:
    base: dict = {
        "src_ip": "",
        "dst_ip": "192.168.56.10",
        "src_port": 0,
        "dst_port": 0,
        "protocol": "TCP",
        "flags": "S",
        "payload_size": 64,
    }

    if attack_type == "normal":
        return [
            {**base, "src_ip": "10.10.10.10", "src_port": 50000 + i, "dst_port": port, "flags": "A", "payload_size": 256}
            for i, port in enumerate([80, 443, 443], start=1)
        ]

    if attack_type == "port-scan":
        return [
            {**base, "src_ip": "10.10.10.30", "src_port": 52000 + i, "dst_port": port}
            for i, port in enumerate([22, 80, 443, 8080, 8443], start=1)
        ]

    if attack_type == "ssh-bruteforce":
        return [
            {**base, "src_ip": "10.10.10.40", "src_port": 53000 + i, "dst_port": 22}
            for i in range(1, 6)
        ]

    if attack_type == "blacklist":
        return [{**base, "src_ip": BLACKLIST_IP, "src_port": 54001, "dst_port": 443}]

    # full-demo
    payloads: list[dict] = []
    for t in ("normal", "port-scan", "ssh-bruteforce", "blacklist"):
        payloads.extend(build_payloads(t))
    return payloads


def _run_scenario_sync(db: Session, attack_type: str) -> dict:
    sensor = ensure_demo_data(db)
    payloads = build_payloads(attack_type)

    total_alerts = 0
    for payload in payloads:
        log = NetworkLog(
            sensor_id=sensor.id,
            timestamp=datetime.now(timezone.utc),
            src_ip=payload["src_ip"],
            dst_ip=payload["dst_ip"],
            src_port=str(payload["src_port"]),
            dst_port=str(payload["dst_port"]),
            protocol=payload.get("protocol", "TCP"),
            flags=payload.get("flags", "S"),
            payload_size=payload.get("payload_size", 64),
        )
        db.add(log)
        db.flush()
        alerts = detect_alerts(db, log, sensor.name)
        total_alerts += len(alerts)

    db.commit()
    return {
        "scenario": attack_type,
        "payloads_sent": len(payloads),
        "alerts_created": total_alerts,
    }


def run_scenario(db: Session, attack_type: str) -> dict:
    if attack_type not in ALLOWED_SCENARIOS:
        raise ValueError(f"Unknown scenario: {attack_type!r}")
    return _run_scenario_sync(db, attack_type)


# ── auto-attack state ─────────────────────────────────────────────────────────

_running: bool = False
_interval: int = 30
_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]
_last_scenario: Optional[str] = None
_last_result: Optional[dict] = None
_next_run_at: Optional[datetime] = None


def get_status() -> dict:
    now = datetime.now(timezone.utc)
    seconds_remaining: Optional[int] = None
    if _running and _next_run_at is not None:
        delta = (_next_run_at - now).total_seconds()
        seconds_remaining = max(0, int(delta))

    return {
        "running": _running,
        "interval_seconds": _interval,
        "next_run_at": _next_run_at.isoformat() if _next_run_at else None,
        "seconds_remaining": seconds_remaining,
        "last_scenario": _last_scenario,
        "last_result": _last_result,
    }


async def _auto_loop() -> None:
    global _next_run_at, _last_scenario, _last_result
    while True:
        _next_run_at = datetime.now(timezone.utc) + timedelta(seconds=_interval)
        await asyncio.sleep(_interval)

        scenario = random.choice(AUTO_SCENARIOS)
        db = SessionLocal()
        try:
            result = _run_scenario_sync(db, scenario)
            _last_scenario = scenario
            _last_result = result
        except Exception:
            pass
        finally:
            db.close()


def start_auto(interval_seconds: int = 30) -> None:
    global _running, _interval, _task, _next_run_at
    _interval = interval_seconds
    _running = True
    _next_run_at = datetime.now(timezone.utc) + timedelta(seconds=interval_seconds)

    if _task is not None and not _task.done():
        _task.cancel()

    _task = asyncio.create_task(_auto_loop())


def stop_auto() -> None:
    global _running, _task, _next_run_at
    _running = False
    _next_run_at = None

    if _task is not None and not _task.done():
        _task.cancel()
    _task = None
