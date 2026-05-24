"""Tests for fingerprint-based alert deduplication with count and last_seen tracking."""
import datetime

import pytest
from sqlalchemy.orm import Session

from app.db.entities.alert import Alert
from app.db.entities.rule import Rule, Match
from app.db.entities.network_log import NetworkLog
from app.services.detection_engine import detect_alerts, _make_fingerprint
from app.shared_models import RuleType, Severity, Protocol, AlertStatus


def _make_rule(db: Session) -> Rule:
    rule = Rule(
        name="Test Blacklist",
        type=RuleType.blacklist_ip,
        enabled=True,
        severity=Severity.high,
        description="test",
    )
    db.add(rule)
    db.flush()
    match = Match(rule_id=rule.id, src_ip="1.2.3.4", protocol=Protocol.TCP)
    db.add(match)
    db.flush()
    return rule


def _make_log(src_ip: str = "1.2.3.4") -> NetworkLog:
    return NetworkLog(
        sensor_id=1,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        src_ip=src_ip,
        dst_ip="10.0.0.1",
        src_port="12345",
        dst_port="80",
        protocol=Protocol.TCP,
        flags="",
        payload_size=100,
    )


def test_fingerprint_is_deterministic():
    fp1 = _make_fingerprint(rule_id=1, src_ip="1.2.3.4", dst_ip="10.0.0.1", protocol="TCP")
    fp2 = _make_fingerprint(rule_id=1, src_ip="1.2.3.4", dst_ip="10.0.0.1", protocol="TCP")
    assert fp1 == fp2


def test_fingerprint_differs_for_different_inputs():
    fp1 = _make_fingerprint(rule_id=1, src_ip="1.2.3.4", dst_ip="10.0.0.1", protocol="TCP")
    fp2 = _make_fingerprint(rule_id=1, src_ip="9.9.9.9", dst_ip="10.0.0.1", protocol="TCP")
    assert fp1 != fp2


def test_dedup_increments_count(auth_client):
    client, Session = auth_client
    with Session() as db:
        rule = _make_rule(db)
        log1 = _make_log()
        db.add(log1)
        db.flush()

        alerts1 = detect_alerts(db, log1, "sensor-a")
        db.commit()

        assert len(alerts1) == 1
        alert_id = alerts1[0].id
        db.refresh(alerts1[0])
        assert alerts1[0].count == 1
        assert alerts1[0].last_seen is None

        log2 = _make_log()
        db.add(log2)
        db.flush()
        alerts2 = detect_alerts(db, log2, "sensor-a")
        db.commit()

        assert len(alerts2) == 1
        assert alerts2[0].id == alert_id
        db.refresh(alerts2[0])
        assert alerts2[0].count == 2
        assert alerts2[0].last_seen is not None
