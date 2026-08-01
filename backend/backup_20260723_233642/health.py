"""
Health Check - Comprehensive system health
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db, health_check_db
from app.core.logging import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)

# Track startup time for uptime
startup_time = time.time()


@router.get("", summary="Health Check")
@router.get("/", summary="Health Check", include_in_schema=False)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check - DB, Supabase, Gemini, n8n"""
    
    checks = {}
    overall_status = "healthy"
    
    # Database
    try:
        db_health = await health_check_db()
        checks["database"] = db_health
        if db_health.get("status") != "healthy":
            overall_status = "degraded"
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "degraded"
    
    # Supabase
    try:
        from app.integrations.supabase_client import health_check_supabase
        supabase_health = await health_check_supabase()
        checks["supabase"] = supabase_health
        if supabase_health.get("status") == "unhealthy":
            overall_status = "degraded"
    except Exception as e:
        checks["supabase"] = {"status": "unhealthy", "error": str(e)}
    
    # Gemini
    try:
        from app.integrations.gemini_client import get_gemini_client
        gemini_client = get_gemini_client()
        if gemini_client.is_configured():
            # Light check - don't call API for health to avoid quota
            checks["gemini"] = {"status": "configured", "model": settings.GEMINI_MODEL}
        else:
            checks["gemini"] = {"status": "not_configured", "message": "GEMINI_API_KEY missing"}
    except Exception as e:
        checks["gemini"] = {"status": "unhealthy", "error": str(e)}
    
    # n8n
    try:
        from app.integrations.n8n_client import health_check_n8n
        n8n_health = await health_check_n8n()
        checks["n8n"] = n8n_health
        # n8n not critical - don't degrade overall status
    except Exception as e:
        checks["n8n"] = {"status": "unknown", "error": str(e)}
    
    # Scheduler
    try:
        from app.tasks.scheduler import get_scheduler
        sched = get_scheduler()
        if sched and sched.running:
            checks["scheduler"] = {"status": "healthy", "jobs": len(sched.get_jobs())}
        else:
            checks["scheduler"] = {"status": "not_running" if not settings.ENABLE_SCHEDULER else "stopped"}
    except Exception as e:
        checks["scheduler"] = {"status": "unknown", "error": str(e)}
    
    uptime = time.time() - startup_time
    
    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(uptime, 2),
        "checks": checks,
        "division": "Nagpur City",
        "phase": "MVP",
    }


@router.get("/ready", summary="Readiness Probe")
async def readiness_check():
    """Kubernetes readiness probe - lightweight"""
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/live", summary="Liveness Probe")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat(), "uptime": time.time() - startup_time}
