"""
Integrations API - Google Forms, Sheets, n8n
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.dependencies.auth import get_current_active_user
from app.dependencies.roles import require_permission
from app.constants.roles import Permission
from app.models.user import User
from app.integrations.google_forms import GoogleFormsIntegration
from app.integrations.google_sheets import get_sheets_client
from app.integrations.n8n_client import trigger_n8n_workflow

router = APIRouter()
settings = get_settings()


@router.post("/forms/webhook", summary="Google Forms Webhook Receiver")
async def forms_webhook(
    request: Request,
    x_webhook_secret: Optional[str] = Header(default=None, alias="X-Webhook-Secret"),
    db: AsyncSession = Depends(get_db),
):
    """
    Receive webhook from Google Forms Apps Script.
    No auth required but validates secret if configured.
    Converts form response to achievement.
    """
    
    payload = await request.json()
    
    # Validate secret
    is_valid = await GoogleFormsIntegration.validate_webhook_secret(x_webhook_secret)
    if not is_valid:
        raise UnauthorizedException("Invalid webhook secret")
    
    try:
        # Parse form
        parsed = GoogleFormsIntegration.parse_form_response(payload)
        
        if not parsed.get("office_code") or not parsed.get("scheme_code"):
            raise BadRequestException("Missing office_code or scheme_code in form response")
        
        # Lookup office and scheme
        from sqlalchemy import select
        from app.models.office import Office
        from app.models.target import Scheme, Target, TargetAllocation
        
        office_result = await db.execute(select(Office).where(Office.office_code == parsed["office_code"]))
        office = office_result.scalars().first()
        if not office:
            raise BadRequestException(f"Office code {parsed['office_code']} not found")
        
        scheme_result = await db.execute(select(Scheme).where(Scheme.scheme_code == parsed["scheme_code"]))
        scheme = scheme_result.scalars().first()
        if not scheme:
            raise BadRequestException(f"Scheme code {parsed['scheme_code']} not found")
        
        # Find allocation - simplified: first allocation for office + scheme + current FY
        from app.utils.helpers import get_financial_year
        current_fy = get_financial_year()
        alloc_result = await db.execute(
            select(TargetAllocation).where(
                TargetAllocation.office_id == office.id,
                TargetAllocation.scheme_id == scheme.id,
                TargetAllocation.financial_year == current_fy
            ).limit(1)
        )
        allocation = alloc_result.scalars().first()
        if not allocation:
            raise BadRequestException(f"No allocation found for office {office.office_code} and scheme {scheme.scheme_code} in FY {current_fy}")
        
        # Get target
        target_result = await db.execute(select(Target).where(Target.id == allocation.target_id))
        target = target_result.scalars().first()
        
        # Map to achievement
        achievement_data = GoogleFormsIntegration.map_to_achievement(
            parsed=parsed,
            office_id=office.id,
            scheme_id=scheme.id,
            allocation_id=allocation.id,
            target_id=target.id if target else allocation.target_id,
        )
        
        # Create achievement via service
        from app.schemas.target import AchievementCreate
        from app.services.target_service import TargetService
        
        ach_create = AchievementCreate(**achievement_data)
        target_service = TargetService(db)
        achievement = await target_service.record_achievement(ach_create)
        
        return {
            "success": True,
            "message": "Achievement recorded from Google Form",
            "data": {
                "achievement_id": achievement.id,
                "office_code": parsed["office_code"],
                "scheme_code": parsed["scheme_code"],
                "amount": parsed["amount"],
            }
        }
    
    except Exception as e:
        # Log but return 200 to avoid Apps Script retries flooding? No, return error
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process form webhook",
        }


@router.get("/sheets/status", summary="Google Sheets Status")
async def sheets_status(
    current_user: User = Depends(require_permission(Permission.INTEGRATION_READ)),
):
    client = get_sheets_client()
    return {
        "success": True,
        "data": {
            "configured": client.is_configured(),
            "enabled": settings.ENABLE_GOOGLE_SHEETS_SYNC,
            "message": "Configured" if client.is_configured() else "Set GOOGLE_SHEETS_CREDENTIALS_JSON",
        }
    }


@router.post("/sheets/read", summary="Read Google Sheet")
async def read_sheet(
    payload: Dict[str, Any],
    current_user: User = Depends(require_permission(Permission.INTEGRATION_READ)),
):
    """
    payload: { "spreadsheet_id": "...", "range": "Sheet1!A1:Z100" }
    """
    spreadsheet_id = payload.get("spreadsheet_id")
    range_name = payload.get("range", "Sheet1!A1:Z100")
    
    if not spreadsheet_id:
        raise BadRequestException("spreadsheet_id required")
    
    client = get_sheets_client()
    if not client.is_configured():
        raise BadRequestException("Google Sheets not configured")
    
    data = await client.read_sheet(spreadsheet_id, range_name)
    
    return {
        "success": True,
        "data": {
            "spreadsheet_id": spreadsheet_id,
            "range": range_name,
            "rows": len(data),
            "data": data[:20],  # First 20 rows for preview
        }
    }


@router.post("/n8n/trigger", summary="Trigger n8n Workflow")
async def trigger_workflow(
    payload: Dict[str, Any],
    current_user: User = Depends(require_permission(Permission.INTEGRATION_MANAGE)),
):
    """
    Manually trigger n8n workflow
    payload: { "event": "notification", "webhook_path": "my-workflow", "data": {...} }
    """
    event = payload.get("event", "manual_trigger")
    webhook_path = payload.get("webhook_path")
    data = payload.get("data", {})
    
    result = await trigger_n8n_workflow(event=event, payload=data, webhook_path=webhook_path)
    
    return {
        "success": result.get("status") == "success",
        "data": result,
    }


@router.get("/status", summary="All Integrations Status")
async def all_integrations_status(
    current_user: User = Depends(require_permission(Permission.INTEGRATION_READ)),
):
    from app.integrations.supabase_client import health_check_supabase
    from app.integrations.gemini_client import get_gemini_client
    from app.integrations.n8n_client import health_check_n8n
    from app.integrations.google_sheets import get_sheets_client
    
    supabase_health = await health_check_supabase()
    
    gemini_client = get_gemini_client()
    gemini_health = await gemini_client.health_check() if gemini_client.is_configured() else {"status": "not_configured"}
    
    n8n_health = await health_check_n8n()
    sheets_client = get_sheets_client()
    
    return {
        "success": True,
        "data": {
            "supabase": supabase_health,
            "gemini": {
                "configured": gemini_client.is_configured(),
                "enabled": settings.ENABLE_AI_CHATBOT,
                "model": settings.GEMINI_MODEL,
                "health": gemini_health,
            },
            "google_sheets": {
                "configured": sheets_client.is_configured(),
                "enabled": settings.ENABLE_GOOGLE_SHEETS_SYNC,
            },
            "google_forms": {
                "enabled": settings.ENABLE_GOOGLE_FORMS_SYNC,
                "webhook_configured": bool(settings.GOOGLE_FORMS_WEBHOOK_SECRET),
            },
            "n8n": n8n_health,
        }
    }
