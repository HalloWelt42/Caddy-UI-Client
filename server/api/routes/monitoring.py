"""
Monitoring API Routes
"""
from fastapi import APIRouter, HTTPException, WebSocket
from typing import List, Dict, Any

from server.api.services import monitor_service

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

@router.get("/metrics")
async def get_current_metrics():
    """Aktuelle System-Metriken abrufen"""
    metrics = await monitor_service.get_current_metrics()
    return metrics

@router.get("/metrics/history")
async def get_metrics_history():
    """Metrik-Historie abrufen"""
    history = monitor_service.get_metrics_history()
    return history

@router.websocket("/metrics/stream")
async def metrics_stream(websocket: WebSocket):
    """WebSocket für Live-Metriken"""
    await websocket.accept()

    try:
        while True:
            metrics = await monitor_service.get_current_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(settings.monitor_interval)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@router.get("/docker/containers")
async def get_docker_containers():
    """Docker-Container auflisten"""
    containers = await monitor_service.get_docker_containers()
    return containers

@router.post("/docker/containers/{container_id}/{action}")
async def control_docker_container(container_id: str, action: str):
    """Docker-Container steuern (start/stop/restart)"""
    if action not in ["start", "stop", "restart"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    result = await monitor_service.control_docker_container(container_id, action)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result

import asyncio
from server.config.settings import settings