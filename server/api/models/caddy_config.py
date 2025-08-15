"""
Pydantic Models für Caddy-Konfiguration
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class CaddyStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    NOT_INSTALLED = "not_installed"
    ERROR = "error"

class RouteRequest(BaseModel):
    """Model für neue Route"""
    domain: str = Field(..., description="Domain/Host für die Route")
    upstream: str = Field(..., description="Upstream-Server (z.B. localhost:3000)")
    path: str = Field(default="/", description="Pfad für die Route")

class RouteResponse(BaseModel):
    """Model für Route-Response"""
    domain: str
    upstream: str
    path: str

class StatusResponse(BaseModel):
    """Model für Status-Response"""
    status: CaddyStatus
    message: str
    admin_api: Optional[bool] = None
    pid: Optional[int] = None
    config: Optional[Dict[str, Any]] = None

class OperationResponse(BaseModel):
    """Model für allgemeine Operation-Response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class BackupRequest(BaseModel):
    """Model für Backup-Request"""
    name: Optional[str] = None

class RestoreRequest(BaseModel):
    """Model für Restore-Request"""
    backup_name: str

class InstallProgress(BaseModel):
    """Model für Installations-Fortschritt"""
    message: str
    progress: int  # 0-100