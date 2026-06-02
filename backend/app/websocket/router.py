from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import asyncio
import json

router = APIRouter()

_dashboard_connections: list[WebSocket] = []
_alert_connections: list[WebSocket] = []


@router.websocket("/dashboard")
async def ws_dashboard(websocket: WebSocket):
    """실시간 KPI 대시보드 스트림"""
    await websocket.accept()
    _dashboard_connections.append(websocket)
    try:
        while True:
            # 5초마다 KPI 더미 데이터 전송 (실제: DB/Redis 폴링)
            payload = {
                "type": "KPI_UPDATE",
                "data": {
                    "hourly_output": 0,
                    "defect_rate": 0,
                    "equipment_oee": 0,
                    "active_work_orders": 0,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        _dashboard_connections.remove(websocket)


@router.websocket("/equipment/{equipment_id}")
async def ws_equipment(websocket: WebSocket, equipment_id: str):
    """특정 설비 센서 실시간 스트림"""
    await websocket.accept()
    try:
        while True:
            payload = {
                "type": "SENSOR_UPDATE",
                "equipment_id": equipment_id,
                "data": {"pressure_mpa": None, "speed_mpm": None, "anomaly_flag": False},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass


@router.websocket("/alerts")
async def ws_alerts(websocket: WebSocket):
    """이상 알림 실시간 수신"""
    await websocket.accept()
    _alert_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        _alert_connections.remove(websocket)


async def broadcast_alert(alert: dict):
    """서버에서 알림 브로드캐스트 (설비 이상 등 발생 시 호출)"""
    dead = []
    for ws in _alert_connections:
        try:
            await ws.send_text(json.dumps({"type": "ALERT", **alert}))
        except Exception:
            dead.append(ws)
    for ws in dead:
        _alert_connections.remove(ws)
