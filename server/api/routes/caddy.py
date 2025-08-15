"""
Caddy API Routes
"""
from fastapi import APIRouter, HTTPException, WebSocket
from typing import List
import json

from server.api.models.caddy_config import (
    RouteRequest, RouteResponse, StatusResponse,
    OperationResponse, BackupRequest, RestoreRequest
)
from server.api.services import caddy_service

router = APIRouter(prefix="/api/caddy", tags=["caddy"])

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Caddy-Status abrufen"""
    status = await caddy_service.get_status()
    return StatusResponse(**status)

@router.post("/install")
async def install_caddy():
    """Caddy installieren"""
    # Einfache Installation ohne Progress-Tracking
    result = await caddy_service.install_caddy()
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.websocket("/install/progress")
async def install_progress(websocket: WebSocket):
    """WebSocket für Installations-Fortschritt"""
    await websocket.accept()

    async def progress_callback(message: str, progress: int):
        await websocket.send_json({
            "message": message,
            "progress": progress
        })

    try:
        result = await caddy_service.install_caddy(progress_callback)
        await websocket.send_json({
            "complete": True,
            "result": result
        })
    except Exception as e:
        await websocket.send_json({
            "error": str(e)
        })
    finally:
        await websocket.close()

@router.post("/start", response_model=OperationResponse)
async def start_caddy():
    """Caddy starten"""
    result = await caddy_service.start()
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.post("/stop", response_model=OperationResponse)
async def stop_caddy():
    """Caddy stoppen"""
    result = await caddy_service.stop()
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.post("/restart", response_model=OperationResponse)
async def restart_caddy():
    """Caddy neu starten"""
    result = await caddy_service.restart()
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.get("/routes", response_model=List[RouteResponse])
async def get_routes():
    """Alle Routes abrufen"""
    routes = await caddy_service.get_routes()
    return [RouteResponse(**route) for route in routes]

@router.post("/routes", response_model=OperationResponse)
async def add_route(route: RouteRequest):
    """Neue Route hinzufügen"""
    result = await caddy_service.add_route(
        domain=route.domain,
        upstream=route.upstream,
        path=route.path
    )
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.delete("/routes/{domain}", response_model=OperationResponse)
async def remove_route(domain: str):
    """Route entfernen"""
    result = await caddy_service.remove_route(domain)
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=404, detail=result.get("error"))

@router.post("/backup", response_model=OperationResponse)
async def backup_config(request: BackupRequest):
    """Konfiguration sichern"""
    result = await caddy_service.backup_config(request.name)
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.post("/restore", response_model=OperationResponse)
async def restore_config(request: RestoreRequest):
    """Konfiguration wiederherstellen"""
    result = await caddy_service.restore_config(request.backup_name)
    if result["success"]:
        return OperationResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))

@router.get("/backups")
async def list_backups():
    """Liste aller Backups"""
    from pathlib import Path
    from server.config.settings import settings

    backups = []
    for backup_file in settings.backups_dir.glob("caddy_config_*.json"):
        backups.append({
            "name": backup_file.name,
            "size": backup_file.stat().st_size,
            "modified": backup_file.stat().st_mtime
        })

    return backups