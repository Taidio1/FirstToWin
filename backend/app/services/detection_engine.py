from datetime import datetime, timedelta, timezone

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.db.entities import Alert, NetworkLog, Rule
from app.shared_models import AlertStatus, RuleType


def detect_alerts(db: Session, log: NetworkLog, sensor_name: str) -> list[Alert]:
    alerts: list[Alert] = []
    rules = db.scalars(select(Rule).where(Rule.enabled.is_(True))).all()

    for rule in rules:
        if rule.type == RuleType.port_scan and _is_port_scan(db, rule, log):
            alerts.append(
                _build_alert(
                    rule,
                    log,
                    sensor_name,
                    "Source contacted many destination ports in a short window.",
                )
            )
        elif rule.type == RuleType.connection_threshold and _is_ssh_bruteforce(db, rule, log):
            alerts.append(
                _build_alert(
                    rule,
                    log,
                    sensor_name,
                    "Multiple SSH connection attempts exceeded the demo threshold.",
                )
            )
        elif rule.type == RuleType.blacklist_ip and _is_blacklisted(rule, log):
            alerts.append(
                _build_alert(
                    rule,
                    log,
                    sensor_name,
                    "Traffic involved the configured blacklisted demo IP.",
                )
            )

    for alert in alerts:
        db.add(alert)

    return alerts


def _window_start(rule: Rule) -> datetime:
    seconds = rule.match.window_seconds if rule.match and rule.match.window_seconds else 60
    return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=seconds)


def _is_port_scan(db: Session, rule: Rule, log: NetworkLog) -> bool:
    if not rule.match or str(log.protocol) != str(rule.match.protocol):
        return False

    threshold = rule.match.threshold or 5
    count = db.scalar(
        select(func.count(distinct(NetworkLog.dst_port))).where(
            NetworkLog.src_ip == log.src_ip,
            NetworkLog.protocol == log.protocol,
            NetworkLog.timestamp >= _window_start(rule),
        )
    )
    return (count or 0) >= threshold


def _is_ssh_bruteforce(db: Session, rule: Rule, log: NetworkLog) -> bool:
    if not rule.match or str(log.dst_port) != str(rule.match.dst_port or 22):
        return False

    threshold = rule.match.threshold or 5
    count = db.scalar(
        select(func.count()).select_from(NetworkLog).where(
            NetworkLog.src_ip == log.src_ip,
            NetworkLog.dst_port == str(rule.match.dst_port or 22),
            NetworkLog.protocol == log.protocol,
            NetworkLog.timestamp >= _window_start(rule),
        )
    )
    return (count or 0) >= threshold


def _is_blacklisted(rule: Rule, log: NetworkLog) -> bool:
    if not rule.match:
        return False

    values = {rule.match.src_ip, rule.match.dst_ip} - {None, ""}
    return log.src_ip in values or log.dst_ip in values


def _build_alert(rule: Rule, log: NetworkLog, sensor_name: str, details: str) -> Alert:
    return Alert(
        rule_id=rule.id,
        rule_name=rule.name,
        severity=str(rule.severity.value if hasattr(rule.severity, "value") else rule.severity),
        status=AlertStatus.open.value,
        src_ip=log.src_ip,
        dst_ip=log.dst_ip,
        protocol=str(log.protocol.value if hasattr(log.protocol, "value") else log.protocol),
        sensor_id=sensor_name,
        details=details,
    )
