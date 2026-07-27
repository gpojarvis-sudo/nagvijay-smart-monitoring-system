"""
Settings API - Admin settings for division config
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.roles import require_permission
from app.constants.roles import Permission
from app.models.user import User
from app.repositories.audit_repository import AuditRepository

router = APIRouter()
app_settings = get_settings()


@router.get("", response_model=dict, summary="Get System Settings")
async def get_settings_api(
    current_user: User = Depends(require_permission(Permission.SETTINGS_MANAGE)),
):
    return {
        "success": True,
        "data": {
            "app": {
                "name": app_settings.APP_NAME,
                "version": app_settings.APP_VERSION,
                "environment": app_settings.APP_ENV,
                "division": "Nagpur City",
                "region": "Nagpur",
                "circle": "Maharashtra",
            },
            "features": {
                "google_forms_sync": app_settings.ENABLE_GOOGLE_FORMS_SYNC,
                "google_sheets_sync": app_settings.ENABLE_GOOGLE_SHEETS_SYNC,
                "ai_chatbot": app_settings.ENABLE_AI_CHATBOT,
                "notifications": app_settings.ENABLE_NOTIFICATIONS,
                "scheduler": app_settings.ENABLE_SCHEDULER,
                "audit_logs": app_settings.ENABLE_AUDIT_LOGS,
            },
            "integrations": {
                "supabase_configured": bool(app_settings.SUPABASE_URL and app_settings.SUPABASE_SERVICE_ROLE_KEY),
                "gemini_configured": bool(app_settings.GEMINI_API_KEY),
                "n8n_configured": bool(app_settings.N8N_WEBHOOK_URL),
                "n8n_enabled": app_settings.N8N_ENABLED,
            },
            "security": {
                "jwt_algorithm": app_settings.JWT_ALGORITHM,
                "access_token_expire_minutes": app_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
                "rate_limit_enabled": app_settings.RATE_LIMIT_ENABLED,
            },
        },
    }


@router.get("/frontend-config", response_model=dict, summary="Get Frontend Config")
async def get_frontend_config():
    return {
        "success": True,
        "data": {
            "app_name": app_settings.APP_NAME,
            "app_version": app_settings.APP_VERSION,
            "environment": app_settings.APP_ENV,
            "supabase_url": app_settings.SUPABASE_URL,
            "supabase_anon_key": app_settings.SUPABASE_ANON_KEY,
            "division": "Nagpur City",
            "region": "Nagpur",
            "circle": "Maharashtra",
            "financial_year": "2024-25",
            "features": {
                "ai_chatbot": app_settings.ENABLE_AI_CHATBOT,
                "notifications": app_settings.ENABLE_NOTIFICATIONS,
            },
        },
    }


@router.get("/audit", response_model=dict, summary="List Audit Logs")
async def list_audit(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    resource_type: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
):
    repo = AuditRepository(db)
    filters = {}
    if resource_type:
        filters["resource_type"] = resource_type
    if action:
        filters["action"] = action

    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by="created_at", order_desc=True)

    data = []
    for log in items:
        data.append(
            {
                "id": log.id,
                "user_email": log.user_email,
                "user_role": log.user_role,
                "action": log.action.value if hasattr(log.action, "value") else str(log.action),
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
        )

    return {
        "success": True,
        "data": data,
        "pagination": {"total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size},
    }
