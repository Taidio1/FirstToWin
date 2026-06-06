from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.entities import Alert, NetworkLog, ScenarioLabel


def _naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=None)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def top_suspicious_ips(db: Session) -> list[dict]:
    alerts = db.scalars(select(Alert)).all()
    by_ip: dict[str, list[Alert]] = defaultdict(list)
    for alert in alerts:
        by_ip[alert.src_ip].append(alert)

    rows = []
    for src_ip, items in by_ip.items():
        hits = sum(a.count for a in items)
        critical = sum(1 for a in items if a.severity == "critical")
        high = sum(1 for a in items if a.severity == "high")
        rules_count = len({a.rule_name for a in items})
        created = [_naive(a.created_at) for a in items if a.created_at]
        seen = [_naive(a.last_seen or a.created_at) for a in items if (a.last_seen or a.created_at)]
        risk = round(critical * 3 + high * 2 + hits * 0.2 + rules_count, 1)
        rows.append({
            "src_ip": src_ip,
            "alerts_count": len(items),
            "hits_count": hits,
            "critical_alerts": critical,
            "high_alerts": high,
            "rules_count": rules_count,
            "risk_score": risk,
            "first_seen": _iso(min(created)) if created else None,
            "last_seen": _iso(max(seen)) if seen else None,
        })

    rows.sort(key=lambda r: (r["risk_score"], r["alerts_count"], r["hits_count"]), reverse=True)
    return rows


def rules_summary(db: Session) -> list[dict]:
    alerts = db.scalars(select(Alert)).all()
    groups: dict[tuple[str, str], list[Alert]] = defaultdict(list)
    for alert in alerts:
        groups[(alert.rule_name, alert.severity)].append(alert)

    rows = []
    for (rule_name, severity), items in groups.items():
        created = [_naive(a.created_at) for a in items if a.created_at]
        seen = [_naive(a.last_seen or a.created_at) for a in items if (a.last_seen or a.created_at)]
        rows.append({
            "rule_name": rule_name,
            "severity": severity,
            "alerts_count": len(items),
            "hits_count": sum(a.count for a in items),
            "src_ip_count": len({a.src_ip for a in items}),
            "first_seen": _iso(min(created)) if created else None,
            "last_seen": _iso(max(seen)) if seen else None,
        })

    rows.sort(key=lambda r: (r["hits_count"], r["alerts_count"]), reverse=True)
    return rows


def _match_scenario(labels, src_ip: str, when: datetime | None) -> str:
    when = _naive(when)
    for label in labels:
        ips = {ip.strip() for ip in (label.src_ip or "").split(";") if ip.strip()}
        if src_ip not in ips:
            continue
        start = _naive(label.starts_at)
        end = _naive(label.ends_at)
        if when is not None and start is not None and end is not None:
            if not (start <= when <= end):
                continue
        return label.scenario
    return "unlabeled"


def scenario_summary(db: Session) -> list[dict]:
    labels = db.scalars(select(ScenarioLabel)).all()
    logs = db.scalars(select(NetworkLog)).all()
    alerts = db.scalars(select(Alert)).all()

    log_groups: dict[str, list] = defaultdict(list)
    for log in logs:
        log_groups[_match_scenario(labels, log.src_ip, log.timestamp)].append(log)

    alert_counts: dict[str, int] = defaultdict(int)
    for alert in alerts:
        alert_counts[_match_scenario(labels, alert.src_ip, alert.created_at)] += 1

    scenarios = set(log_groups) | set(alert_counts)
    rows = []
    for scenario in scenarios:
        items = log_groups.get(scenario, [])
        payloads = [log.payload_size for log in items if log.payload_size is not None]
        rows.append({
            "scenario": scenario,
            "logs_count": len(items),
            "src_ip_count": len({log.src_ip for log in items}),
            "dst_ip_count": len({log.dst_ip for log in items}),
            "dst_port_count": len({log.dst_port for log in items}),
            "avg_payload_size": round(sum(payloads) / len(payloads), 1) if payloads else None,
            "alerts_count": alert_counts.get(scenario, 0),
        })

    rows.sort(key=lambda r: (r["scenario"] == "normal", -r["alerts_count"], -r["logs_count"]))
    return rows
