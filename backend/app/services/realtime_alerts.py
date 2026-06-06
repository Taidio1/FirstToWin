from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import WebSocket

from app.db.entities.alert import Alert


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def serialize_alert(alert: Alert) -> dict[str, Any]:
    return {
        "id": alert.id,
        "rule_id": alert.rule_id,
        "rule_name": alert.rule_name,
        "severity": alert.severity,
        "status": alert.status,
        "src_ip": alert.src_ip,
        "dst_ip": alert.dst_ip,
        "protocol": alert.protocol,
        "details": alert.details,
        "created_at": _isoformat(alert.created_at),
        "sensor_id": alert.sensor_id,
        "count": alert.count,
        "last_seen": _isoformat(alert.last_seen),
    }


def alert_event_type(alert: Alert) -> str:
    if alert.last_seen is not None or alert.count > 1:
        return "alert.updated"
    return "alert.created"


class AlertBroadcaster:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        await websocket.send_json({"type": "alerts.connected"})

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def publish_alert(self, alert: Alert) -> None:
        await self.broadcast(
            {
                "type": alert_event_type(alert),
                "alert": serialize_alert(alert),
            }
        )

    async def broadcast(self, message: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in list(self._connections):
            try:
                await websocket.send_json(message)
            except RuntimeError:
                stale.append(websocket)

        for websocket in stale:
            self.disconnect(websocket)


alert_broadcaster = AlertBroadcaster()
