from __future__ import annotations

from datetime import datetime
import asyncio

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_sheets import get_sheets_client
from app.models.daily_office_report import DailyOfficeReport
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class DailyOfficeReportSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sheets = get_sheets_client()

    async def sync_pending_reports(self) -> dict:
        if not self.sheets.is_configured():
            logger.warning("google_sheets_not_configured")
            return {
                "total": 0,
                "synced": 0,
                "failed": 0,
                "message": "Google Sheets not configured",
            }

        stmt = (
            select(DailyOfficeReport)
            .where(DailyOfficeReport.sync_status == "PENDING")
            .order_by(DailyOfficeReport.report_date)
        )

        result = await self.db.execute(stmt)
        reports = result.scalars().all()

        synced = 0
        failed = 0

        for report in reports:
            try:
                row = [
                    str(report.report_date),
                    report.office_code,
                    report.office_name,
                    report.sb_opened,
                    report.sb_closed,
                    report.net_accounts,
                    report.pli_policies,
                    float(report.sum_assured),
                    float(report.premium),
                    report.speed_post_document,
                    report.speed_post_parcel,
                    report.business_post,
                    report.logistics,
                    report.international_letter,
                    report.aadhaar_transactions,
                    float(report.aadhaar_amount),
                ]

                await self.sheets.append_row(
                    settings.GOOGLE_SHEETS_SPREADSHEET_ID,
                    "Office wise!A:P",
                    row,
                )

                report.sync_status = "SYNCED"
                report.synced_at = datetime.utcnow()
                report.retry_count = 0
                report.last_sync_error = None

                synced += 1

                # Prevent Google Sheets write quota (60 writes/min/user)
                await asyncio.sleep(1.1)

            except Exception as exc:
                report.sync_status = "FAILED"
                report.retry_count += 1
                report.last_sync_error = str(exc)[:1000]
                failed += 1

                logger.exception(
                    "daily_report_sync_failed",
                    office=report.office_code,
                    error=str(exc),
                )

        await self.db.commit()

        return {
            "total": len(reports),
            "synced": synced,
            "failed": failed,
        }
