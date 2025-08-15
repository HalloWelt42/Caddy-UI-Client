"""
FastAPI Server - Hauptdatei
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn
from contextlib import asynccontextmanager

from server.config.settings import settings
from server.api.routes import caddy, monitoring
from server.api.services.monitor_service import monitor_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle-Management für die App"""
    # Startup
    print(f"🚀 Server startet auf {settings.host}:{settings.port}")
    print(f"📁 Projekt-Root: {settings.project_root}")

    # Monitoring starten
    await monitor_service.start_monitoring()
    print("📊 Monitoring gestartet")

    yield

    # Shutdown
    await monitor_service.stop_monitoring()
    print("👋 Server wird heruntergefahren")


# FastAPI App erstellen
app = FastAPI(
    title="Caddy Manager API",
    description="API zur Verwaltung von Caddy Server",
    version="1.0.0",
    lifespan=lifespan
)

# CORS-Konfiguration für lokale Entwicklung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request-Tracking Middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Trackt Requests für Monitoring"""
    start_time = time.time()

    # Request zählen
    monitor_service.record_request()

    # Response verarbeiten
    response = await call_next(request)

    # Response-Zeit speichern
    process_time = (time.time() - start_time) * 1000  # in ms
    monitor_service.record_response_time(process_time)

    # Header hinzufügen
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Routen einbinden
app.include_router(caddy.router)
app.include_router(monitoring.router)


# Root-Endpoint
@app.get("/")
async def root():
    """Root-Endpoint mit Server-Info"""
    return {
        "name": "Caddy Manager API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "caddy": "/api/caddy",
            "monitoring": "/api/monitoring",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Health-Check
@app.get("/health")
async def health_check():
    """Health-Check Endpoint"""
    caddy_status = await monitor_service._check_caddy_status()
    docker_status = await monitor_service._check_docker_status()

    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "caddy": caddy_status,
            "docker": docker_status
        }
    }


# Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Globaler Exception Handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url)
        }
    )


def run_server():
    """Server starten"""
    uvicorn.run(
        "server.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()