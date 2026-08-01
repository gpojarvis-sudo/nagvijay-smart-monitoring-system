"""
Main API Router - Phase 1 MVP
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    health,
    offices,
    daily_reports,
    reports,
    integrations,
)

api_router = APIRouter()

# Health
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Offices
api_router.include_router(
    offices.router,
    prefix="/offices",
    tags=["Offices"],
)

# Daily Reports
api_router.include_router(
    daily_reports.router,
    prefix="/daily-reports",
    tags=["Daily Reports"],
)

# Reports
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
)

# Google Forms / Sheets Integrations
api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["Integrations"],
)
