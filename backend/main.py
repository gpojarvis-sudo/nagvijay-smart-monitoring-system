"""
NagVijay Smart Monitoring System (NSMS) - Main Application Entry
Enterprise Monitoring Platform for India Post - Nagpur City Division

MVP Phase - Production Ready
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import NSMSException, nsms_exception_handler, validation_exception_handler, http_exception_handler
from app.core.database import init_db, close_db
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.api.v1.router import api_router
from app.tasks.scheduler import init_scheduler, shutdown_scheduler

settings = get_settings()
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan - startup and shutdown"""
    logger.info("starting_nsms", version=settings.APP_VERSION, env=settings.APP_ENV)
    
    # Initialize database
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
        # Don't fail startup, will retry on first request
    
    # Initialize scheduler
    if settings.ENABLE_SCHEDULER:
        try:
            init_scheduler()
            logger.info("scheduler_initialized")
        except Exception as e:
            logger.error("scheduler_init_failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("shutting_down_nsms")
    if settings.ENABLE_SCHEDULER:
        try:
            shutdown_scheduler()
        except Exception:
            pass
    await close_db()
    logger.info("shutdown_complete")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        ## NagVijay Smart Monitoring System (NSMS)
        
        Enterprise Monitoring Platform for India Post.
        
        **Features:**
        - Google Login & JWT Authentication
        - Role Based Access Control
        - Office & Employee Master
        - Target Engine with Google Forms/Sheets Integration
        - Analytics & Reports
        - AI Chatbot (Gemini)
        - Notifications & Scheduler
        - Audit Logs
        
        **Target:** Nagpur City Division (Scalable to Region, Circle, National)
        
        ### Authentication
        Use `/api/v1/auth/google` for Google OAuth.
        Include JWT in header: `Authorization: Bearer <token>`
        
        ### Roles
        - SUPER_ADMIN: Full system access
        - DIVISION_ADMIN: Division-level management
        - OFFICE_ADMIN: Office-level management
        - EMPLOYEE: Own data view/edit
        - AUDITOR: Read-only + audit logs
        """,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        contact={
            "name": "NagVijay NSMS Team",
            "email": "support@nagvijay.india-post",
        },
        license_info={
            "name": "MIT",
        },
    )
    
    # Middleware - Order matters (last added is first executed)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # CORS
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()] if settings.CORS_ORIGINS else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted hosts (production)
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure via env in production
        )
    
    # Exception handlers
    app.add_exception_handler(NSMSException, nsms_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Include API router
    
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

import logging
print("========== REGISTERED ROUTES ==========")
for route in app.routes:
    if hasattr(route, "methods"):
        print(",".join(route.methods), route.path)
print("=======================================")

    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "operational",
            "environment": settings.APP_ENV,
            "docs": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else "disabled in production",
            "health": f"{settings.API_V1_PREFIX}/health",
            "target": "Nagpur City Division - India Post",
            "phase": "MVP - Scalable to National",
        }
    
    @app.get("/health", tags=["Root"])
    async def simple_health():
        return {"status": "ok", "timestamp": time.time()}
    
    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 2,
        log_level=settings.LOG_LEVEL.lower(),
    )
