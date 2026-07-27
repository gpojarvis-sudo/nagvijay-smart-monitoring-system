"""
Sync Tasks - Background jobs for sheets, reports, cleanup
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


async def daily_target_rollover():
    """Daily job - handle target rollover, reset daily counters if needed"""
    logger.info("job_started", job="daily_target_rollover")
    try:
        # In MVP, this is a placeholder for future logic:
        # - Close previous day's pending entries
        # - Notify offices with zero achievement yesterday
        # - Prepare new day's allocation
        
        # Example: Trigger n8n workflow for rollover
        from app.integrations.n8n_client import trigger_n8n_workflow
        await trigger_n8n_workflow(
            event="daily_rollover",
            payload={"date": datetime.utcnow().isoformat(), "division": "Nagpur City"},
            webhook_path="daily-rollover"
        )
        
        logger.info("job_completed", job="daily_target_rollover")
    except Exception as e:
        logger.error("job_failed", job="daily_target_rollover", error=str(e))


async def sync_google_sheets():
    """Sync Google Sheets - import achievements"""
    logger.info("job_started", job="sync_google_sheets")

    try:
        if not settings.ENABLE_GOOGLE_SHEETS_SYNC:
            logger.info("job_skipped", job="sync_google_sheets", reason="disabled")
            return

        from app.core.database import AsyncSessionLocal
        from app.integrations.google_sheets import get_sheets_client
        from app.services.form_import_service import FormImportService

        sheets_client = get_sheets_client()

        if not sheets_client.is_configured():
            logger.warning("sheets_not_configured_skip")
            return

        rows = await sheets_client.parse_achievement_sheet()

        if not rows:
            logger.info("job_completed", job="sync_google_sheets", imported=0)
            return

        processed = 0
        imported = 0
        failed = 0

        async with AsyncSessionLocal() as db:
            for row in rows:
                processed += 1
                try:
                    await FormImportService.process(row, db)
                    imported += 1
                except Exception as exc:
                    failed += 1
                    logger.warning(
                        "sheet_row_failed",
                        row=row.get("_row_number"),
                        error=str(exc),
                    )

        logger.info(
            "job_completed",
            job="sync_google_sheets",
            processed=processed,
            imported=imported,
            failed=failed,
        )

    except Exception as e:
        logger.error(
            "job_failed",
            job="sync_google_sheets",
            error=str(e),
        )


async def send_daily_reports():
    """Generate and send daily reports via n8n/email"""
    logger.info("job_started", job="send_daily_reports")
    try:
        from app.integrations.n8n_client import trigger_report_workflow
        
        # Get division admins emails - would need DB access
        # For now trigger workflow that handles email list internally
        await trigger_report_workflow(
            report_type="DAILY",
            filters={"division": "Nagpur City"},
            recipient_emails=[],  # n8n workflow can fetch from DB
        )
        
        logger.info("job_completed", job="send_daily_reports")
    except Exception as e:
        logger.error("job_failed", job="send_daily_reports", error=str(e))


async def check_pending_verifications():
    """Check and notify about pending verifications"""
    logger.info("job_started", job="check_pending_verifications")
    try:
        # Would query DB for pending verifications > 24h
        # Then notify admins
        
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select, func
        from app.models.target import Achievement
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count()).where(Achievement.is_verified == False)
            )
            pending_count = result.scalar() or 0
            
            if pending_count > 10:
                logger.warning("high_pending_verifications", count=pending_count)
                # Trigger notification
                from app.integrations.n8n_client import trigger_n8n_workflow
                await trigger_n8n_workflow(
                    event="pending_verifications_alert",
                    payload={"count": pending_count, "division": "Nagpur City"},
                    webhook_path="verification-alert"
                )
        
        logger.info("job_completed", job="check_pending_verifications", pending=pending_count if 'pending_count' in locals() else 0)
    
    except Exception as e:
        logger.error("job_failed", job="check_pending_verifications", error=str(e))


async def cleanup_audit_logs():
    """Cleanup audit logs older than 90 days"""
    logger.info("job_started", job="cleanup_audit_logs")
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import delete
        from app.models.audit import AuditLog
        
        cutoff = datetime.utcnow() - timedelta(days=90)
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(AuditLog).where(AuditLog.created_at < cutoff)
            )
            await session.commit()
            logger.info("audit_logs_cleaned", deleted=result.rowcount, cutoff=cutoff.isoformat())
    
    except Exception as e:
        logger.error("job_failed", job="cleanup_audit_logs", error=str(e))
