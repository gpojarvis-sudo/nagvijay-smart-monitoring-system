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
from app.services.form_import_service import FormImportService
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
    Converts form response to DailyOfficeReport.
    """
    
    payload = await request.json()
    
    # Validate secret
    is_valid = await GoogleFormsIntegration.validate_webhook_secret(x_webhook_secret)
    if not is_valid:
        raise UnauthorizedException("Invalid webhook secret")
    
    try:
        from app.services.daily_office_report_service import DailyOfficeReportService
        
        # Parse form payload
        office_code = payload.get("office_code")
        report_date = payload.get("achievement_date") or payload.get("report_date") or datetime.now().strftime("%d.%m.%Y")
        amount = float(payload.get("amount") or 0)
        
        # Find office
        from sqlalchemy import select
        from app.models.office import Office
        office_result = await db.execute(select(Office).where(Office.office_code == office_code))
        office = office_result.scalars().first()
        if not office:
            raise BadRequestException(f"Office code {office_code} not found")
        
        # Prepare data for DailyOfficeReport
        report_data = {
            "office_code": office.office_code,
            "office_name": office.office_name,
            "report_date": report_date,
            "sb_opened": payload.get("sb_opened") or 0,
            "sb_closed": payload.get("sb_closed") or 0,
            "net_accounts": payload.get("net_accounts") or 0,
            "pli_policies": payload.get("pli_policies") or 0,
            "sum_assured": payload.get("sum_assured") or 0.0,
            "premium": payload.get("premium") or 0.0,
            "speed_post_document": payload.get("speed_post_document") or 0,
            "speed_post_parcel": payload.get("speed_post_parcel") or 0,
            "business_post": payload.get("business_post") or 0,
            "logistics": payload.get("logistics") or 0,
            "international_letter": payload.get("international_letter") or 0,
            "aadhaar_transactions": payload.get("aadhaar_transactions") or 0,
            "aadhaar_amount": payload.get("aadhaar_amount") or 0.0,
        }
        
        # Upsert into DailyOfficeReport
        service = DailyOfficeReportService(db)
        report = await service.upsert(report_data)
        
        return {
            "success": True,
            "message": "Daily office report updated from Google Form",
            "data": {
                "report_id": report.id,
                "office_code": office_code,
                "report_date": str(report.report_date),
            }
        }
    
    except Exception as e:
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
    
    try:
        data = await client.read_sheet(spreadsheet_id, range_name)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
        }

    
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


@router.post("/sheets/sync-daily-office-report", summary="Sync Daily Office Report")
async def sync_daily_office_reports_endpoint(
    current_user: User = Depends(require_permission(Permission.INTEGRATION_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    from app.services.google_sheet_sync_service import GoogleSheetSyncService

    service = GoogleSheetSyncService(db)
    result = await service.sync_daily_office_reports()

    return {
        "success": True,
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
