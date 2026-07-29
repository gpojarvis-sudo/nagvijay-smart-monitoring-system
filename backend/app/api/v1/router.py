"""
Main API Router - Aggregates all v1 routes
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, users, offices, employees, targets, analytics, reports, ai, notifications, integrations, health, settings, daily_reports, sync_errors, ai_insights, ai_monitoring, pipeline

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

# Analytics & Reports
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# AI & Notifications
api_router.include_router(ai.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Integrations
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

# Settings
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(daily_reports.router, prefix="/daily-reports", tags=["Daily Reports"])
api_router.include_router(sync_errors.router, prefix="/sync-errors", tags=["Sync Errors"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["AI Insights"])
api_router.include_router(ai_monitoring.router, tags=["AI Monitoring"])
api_router.include_router(pipeline.router, tags=["Pipeline"])

# DIAGNOSTIC: Print pipeline routes after registration
print("🔍 PIPELINE ROUTES:", [route.path for route in pipeline.router.routes])
