"""
Daily Summary Report Task - Generates and logs daily summary at 8 PM
"""
from datetime import date
import structlog
from app.core.database import AsyncSessionLocal
from app.services.daily_office_report_service import DailyOfficeReportService

logger = structlog.get_logger(__name__)

async def generate_daily_summary() -> dict:
    """Generate daily summary for today and log it."""
    async with AsyncSessionLocal() as db:
        service = DailyOfficeReportService(db)
        today = date.today()
        summary = await service.get_summary(today)
        # Log the summary
        logger.info("daily_summary_generated", report_date=today.isoformat(), **summary)
        # Could also store in a report table if needed
        return summary
