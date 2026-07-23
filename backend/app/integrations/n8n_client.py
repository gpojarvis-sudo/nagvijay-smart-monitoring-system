"""
n8n Client - Workflow automation integration
"""
from __future__ import annotations

from typing import Dict, Any, Optional
import uuid

import structlog
import httpx

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


async def trigger_n8n_workflow(event: str, payload: Dict[str, Any], webhook_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Trigger n8n workflow via webhook
    
    n8n webhook URL format: https://your-n8n.com/webhook/<path> or https://your-n8n.com/webhook-test/<path>
    """
    
    if not settings.N8N_ENABLED:
        logger.debug("n8n_disabled", event=event)
        return {"status": "skipped", "reason": "N8N_ENABLED=False"}
    
    if not settings.N8N_WEBHOOK_URL:
        logger.warning("n8n_webhook_url_missing", event=event)
        return {"status": "skipped", "reason": "N8N_WEBHOOK_URL missing"}
    
    # Build URL
    base_url = settings.N8N_WEBHOOK_URL.rstrip("/")
    if webhook_path:
        url = f"{base_url}/{webhook_path.lstrip('/')}"
    else:
        # Default - use event as path
        url = f"{base_url}/{event}"
    
    # Prepare payload
    full_payload = {
        "event": event,
        "timestamp": str(payload.get("timestamp") or __import__("datetime").datetime.utcnow().isoformat()),
        "source": "nagvijay-nsms",
        "division": "Nagpur City",
        "data": payload,
        "id": str(uuid.uuid4()),
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-N8N-Source": "nagvijay-nsms",
        "X-Event-Type": event,
    }
    
    if settings.N8N_API_KEY:
        headers["X-N8N-API-KEY"] = settings.N8N_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=full_payload, headers=headers)
            
            if response.status_code in [200, 201, 202]:
                logger.info("n8n_workflow_triggered", event=event, status=response.status_code, url=url)
                return {"status": "success", "status_code": response.status_code, "response": response.json() if response.content else {}}
            else:
                logger.warning("n8n_workflow_failed", event=event, status=response.status_code, body=response.text[:500])
                return {"status": "failed", "status_code": response.status_code, "error": response.text[:500]}
    
    except httpx.TimeoutException:
        logger.warning("n8n_timeout", event=event, url=url)
        return {"status": "timeout", "event": event}
    except Exception as e:
        logger.error("n8n_error", event=event, error=str(e))
        return {"status": "error", "error": str(e)}


async def trigger_notification_workflow(notification_type: str, recipient_email: str, data: Dict[str, Any]) -> Dict:
    """Specific helper for notification workflows"""
    return await trigger_n8n_workflow(
        event="notification",
        payload={
            "type": notification_type,
            "recipient": recipient_email,
            "subject": data.get("title", "NSMS Notification"),
            "message": data.get("message", ""),
            "action_url": data.get("action_url"),
            "division": data.get("division", "Nagpur City"),
        },
        webhook_path="nsms-notifications"
    )


async def trigger_report_workflow(report_type: str, filters: Dict[str, Any], recipient_emails: list) -> Dict:
    """Trigger scheduled report generation"""
    return await trigger_n8n_workflow(
        event="scheduled_report",
        payload={
            "report_type": report_type,
            "filters": filters,
            "recipients": recipient_emails,
        },
        webhook_path="nsms-reports"
    )


async def trigger_sheets_sync_workflow(spreadsheet_id: str, sync_type: str = "import") -> Dict:
    """Trigger Google Sheets sync"""
    return await trigger_n8n_workflow(
        event="sheets_sync",
        payload={
            "spreadsheet_id": spreadsheet_id,
            "sync_type": sync_type,
        },
        webhook_path="nsms-sheets-sync"
    )


async def health_check_n8n() -> Dict[str, Any]:
    """Check n8n connectivity"""
    if not settings.N8N_ENABLED:
        return {"status": "disabled", "message": "N8N_ENABLED=False"}
    if not settings.N8N_WEBHOOK_URL:
        return {"status": "not_configured", "message": "N8N_WEBHOOK_URL missing"}
    
    try:
        # Try to trigger a health check event
        result = await trigger_n8n_workflow("health_check", {"check": "ping"}, webhook_path="health")
        if result.get("status") in ["success", "timeout"]:
            # timeout might still mean n8n received it
            return {"status": "healthy", "url": settings.N8N_WEBHOOK_URL, "details": result}
        else:
            return {"status": "unhealthy", "details": result}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
