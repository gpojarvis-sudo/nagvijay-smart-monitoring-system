"""
Main API Router - Aggregates all v1 routes
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import users
from app.api.v1 import offices
from app.api.v1 import employees
from app.api.v1 import targets
from app.api.v1 import analytics
from app.api.v1 import reports
from app.api.v1 import ai
from app.api.v1 import notifications
from app.api.v1 import integrations
from app.api.v1 import health
from app.api.v1 import settings
from app.api.v1 import daily_reports
from app.api.v1 import sync_errors
from app.api.v1 import ai_insights
from app.api.v1 import ai_monitoring
from app.api.v1 import pipeline

api_router = APIRouter()

# Health - no auth
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Auth
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Core resources
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(offices.router, prefix="/offices", tags=["Offices"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets & Schemes"])

# Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Reports
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# AI & Notifications
api_router.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Integrations
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

# Settings
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])

# Daily Reports
api_router.include_router(daily_reports.router, prefix="/daily-reports", tags=["Daily Reports"])

# Sync Errors
api_router.include_router(sync_errors.router, prefix="/sync-errors", tags=["Sync Errors"])

# AI Insights
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["AI Insights"])

# AI Monitoring
api_router.include_router(ai_monitoring.router, prefix="/ai-monitoring", tags=["AI Monitoring"])

# Pipeline
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
