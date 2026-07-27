from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.google_sheets import get_sheets_client
from app.services.daily_office_report_service import DailyOfficeReportService


class GoogleSheetSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sheets = get_sheets_client()
        self.daily_service = DailyOfficeReportService(db)

    async def sync_daily_office_reports(self) -> dict:
        reports = await self.sheets.parse_daily_office_report_sheet()

        synced = 0
        failed = 0
        errors = []

        for report in reports:
            try:
                # Pass a fresh session for each report to avoid transaction issues
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as fresh_db:
                    service = DailyOfficeReportService(fresh_db)
                    await service.upsert(report)
                    await fresh_db.commit()
                synced += 1
            except Exception as exc:
                failed += 1
                # Log error to sync_errors table
                from app.models.sync_error import SyncError
                from app.constants.status import SyncErrorType
                from datetime import datetime as dt
                async with AsyncSessionLocal() as log_db:
                    error_log = SyncError(
                        error_date=dt.utcnow().date(),
                        office_name=report.get("office_name_original") or report.get("office_name"),
                        office_code=report.get("office_code"),
                        error_type=SyncErrorType.SYNC,
                        error_message=str(exc)[:500],
                    )
                    log_db.add(error_log)
                    await log_db.commit()
                errors.append(
                    {
                        "row": report.get("_row_number"),
                        "office_code": report.get("office_code"),
                        "error": str(exc),
                    }
                )

        return {
            "total": len(reports),
            "synced": synced,
            "failed": failed,
            "errors": errors,
        }
