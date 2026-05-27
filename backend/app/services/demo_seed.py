from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.entities import Match, Rule, Sensor, User
from app.helpers.login_helper import hash_password
from app.shared_models import Protocol, RuleType, SensorStatus, Severity

DEMO_SENSOR_NAME = "local-demo-sensor"
DEMO_SENSOR_KEY = "demo-sensor-key"
DEMO_BLACKLIST_IP = "203.0.113.66"


def ensure_demo_data(db: Session) -> Sensor:
    sensor = db.scalars(
        select(Sensor).where(Sensor.name == DEMO_SENSOR_NAME)
    ).one_or_none()
    if sensor is None:
        sensor = Sensor(
            name=DEMO_SENSOR_NAME,
            location="local demo",
            api_key=DEMO_SENSOR_KEY,
            status=SensorStatus.online,
        )
        db.add(sensor)
        db.flush()
    elif sensor.api_key != DEMO_SENSOR_KEY:
        sensor.api_key = DEMO_SENSOR_KEY

    user = db.scalars(
        select(User).where(User.email == "demo@example.local")
    ).one_or_none()
    if user is None:
        db.add(
            User(
                email="demo@example.local",
                username="demo",
                role="admin",
                password=hash_password("demo1234"),
            )
        )
    elif user.role not in ("admin", "user"):
        user.role = "admin"

    _ensure_rule(
        db,
        name="Port Scan",
        rule_type=RuleType.port_scan,
        severity=Severity.high,
        description="Detects one source probing many destination ports.",
        match=Match(protocol=Protocol.TCP, threshold=5, window_seconds=60),
    )
    _ensure_rule(
        db,
        name="SSH Brute Force",
        rule_type=RuleType.connection_threshold,
        severity=Severity.critical,
        description="Detects repeated SSH connection attempts from one source.",
        match=Match(protocol=Protocol.TCP, dst_port=22, threshold=5, window_seconds=60),
    )
    _ensure_rule(
        db,
        name="Blacklist IP",
        rule_type=RuleType.blacklist_ip,
        severity=Severity.critical,
        description="Detects traffic involving a known blacklisted demo IP.",
        match=Match(protocol=Protocol.TCP, src_ip=DEMO_BLACKLIST_IP),
    )

    db.commit()
    db.refresh(sensor)
    return sensor


def _ensure_rule(
    db: Session,
    name: str,
    rule_type: RuleType,
    severity: Severity,
    description: str,
    match: Match,
) -> Rule:
    rule = db.scalars(select(Rule).where(Rule.name == name)).one_or_none()
    if rule is not None:
        return rule

    rule = Rule(
        name=name,
        type=rule_type,
        enabled=True,
        severity=severity,
        description=description,
    )
    rule.match = match
    db.add(rule)
    db.flush()
    return rule
