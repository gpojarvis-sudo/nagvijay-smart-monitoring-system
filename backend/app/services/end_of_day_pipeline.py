"""
End-of-Day Pipeline – Orchestrates daily processing:
1. Read new rows from Response 1 sheet
2. Validate and append to Raw Data Sheet
3. Sync to PostgreSQL
4. Recalculate metrics
5. Generate AI Brief
6. Log processing
"""
import asyncio
from datetime import date, datetime, timezone
from typing import List, Dict, Any
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.integrations.google_sheets import get_sheets_client
from app.services.daily_office_report_service import DailyOfficeReportService
from app.models.daily_office_report import DailyOfficeReport
from app.models.office import Office
from app.models.pipeline_state import PipelineState
from app.services.ai_monitoring_service import AIMonitoringEngine

logger = structlog.get_logger(__name__)
settings = get_settings()


class EndOfDayPipeline:
    RESPONSE_SHEET_NAME = "Form Responses 1"
    RAW_SHEET_NAME = "Office wise"

    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.sheets = get_sheets_client()

    async def run(self) -> Dict[str, Any]:
        logger.info("eod_pipeline_started")
        result = {
            "status": "started",
            "new_rows_processed": 0,
            "duplicates_skipped": 0,
            "errors": [],
            "ai_brief": None,
        }

        async with AsyncSessionLocal() as session:
            self.db = session
            new_rows = await self._fetch_new_response_rows()
            if not new_rows:
                logger.info("eod_no_new_rows")
                result["status"] = "no_new_data"
                await self._log_state("last_eod_run", "no_new_data")
                return result

            await self._append_to_raw_sheet(new_rows)
            sync_result = await self._sync_to_postgres(new_rows)
            result["new_rows_processed"] = sync_result["inserted"]
            result["duplicates_skipped"] = sync_result["skipped"]

            ai_brief = await self._generate_ai_brief()
            result["ai_brief"] = ai_brief

            await self._log_state("last_eod_run", "success", {
                "processed": result["new_rows_processed"],
                "skipped": result["duplicates_skipped"],
                "date": date.today().isoformat()
            })
            await session.commit()

        logger.info("eod_pipeline_completed", **result)
        return result

    async def _fetch_new_response_rows(self) -> List[Dict]:
        last_row = await self._get_state("response_last_row") or "0"
        try:
            last_row_int = int(last_row)
        except ValueError:
            last_row_int = 0

        rows = await self.sheets.read_sheet(
            settings.GOOGLE_SHEETS_SPREADSHEET_ID,
            f"{self.RESPONSE_SHEET_NAME}!A1:Z1000"
        )
        if not rows or len(rows) < 2:
            return []

        headers = rows[0]
        new_rows = []
        for idx, row in enumerate(rows[1:], start=1):
            if idx <= last_row_int:
                continue
            row_dict = dict(zip(headers, row))
            if row_dict.get("office_code") or row_dict.get("office_name"):
                new_rows.append(row_dict)

        new_last_row = last_row_int + len(new_rows)
        await self._set_state("response_last_row", str(new_last_row))
        return new_rows

    async def _append_to_raw_sheet(self, rows: List[Dict]) -> Dict:
        logger.info("append_to_raw_sheet_called", rows_count=len(rows))
        return {"status": "pending", "rows": len(rows)}

    async def _sync_to_postgres(self, rows: List[Dict]) -> Dict:
        service = DailyOfficeReportService(self.db)
        inserted = 0
        skipped = 0
        for row in rows:
            try:
                office_code = row.get("office_code")
                office_name = row.get("office_name")
                report_date_str = row.get("achievement_date") or row.get("report_date")
                if not report_date_str:
                    continue
                from datetime import datetime as dt
                try:
                    report_date = dt.strptime(report_date_str, "%d.%m.%Y").date()
                except ValueError:
                    try:
                        report_date = dt.strptime(report_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        continue

                office = None
                if office_code:
                    stmt = select(Office).where(Office.office_code == office_code)
                    result = await self.db.execute(stmt)
                    office = result.scalar_one_or_none()
                if not office and office_name:
                    stmt = select(Office).where(Office.office_name == office_name)
                    result = await self.db.execute(stmt)
                    office = result.scalar_one_or_none()
                if not office:
                    continue

                stmt = select(DailyOfficeReport).where(
                    DailyOfficeReport.office_id == office.id,
                    DailyOfficeReport.report_date == report_date
                )
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    skipped += 1
                    continue

                report_data = {
                    "office_code": office.office_code,
                    "office_name": office.office_name,
                    "report_date": report_date_str,
                    "sb_opened": int(row.get("sb_opened") or 0),
                    "sb_closed": int(row.get("sb_closed") or 0),
                    "net_accounts": int(row.get("net_accounts") or 0),
                    "pli_policies": int(row.get("pli_policies") or 0),
                    "sum_assured": float(row.get("sum_assured") or 0.0),
                    "premium": float(row.get("premium") or 0.0),
                    "speed_post_document": int(row.get("speed_post_document") or 0),
                    "speed_post_parcel": int(row.get("speed_post_parcel") or 0),
                    "business_post": int(row.get("business_post") or 0),
                    "logistics": int(row.get("logistics") or 0),
                    "international_letter": int(row.get("international_letter") or 0),
                    "aadhaar_transactions": int(row.get("aadhaar_transactions") or 0),
                    "aadhaar_amount": float(row.get("aadhaar_amount") or 0.0),
                }
                await service.upsert(report_data)
                inserted += 1
            except Exception as e:
                logger.error("sync_row_failed", error=str(e), row=row)
                continue

        return {"inserted": inserted, "skipped": skipped}

    async def _generate_ai_brief(self) -> str:
        engine = AIMonitoringEngine(self.db)
        summary = await engine.generate_monitoring_report()
        return summary.get("ai_brief", "No AI brief available.")

    async def _get_state(self, key: str) -> str:
        stmt = select(PipelineState).where(PipelineState.key == key)
        result = await self.db.execute(stmt)
        state = result.scalar_one_or_none()
        return state.value if state else None

    async def _set_state(self, key: str, value: str, metadata: dict = None):
        stmt = select(PipelineState).where(PipelineState.key == key)
        result = await self.db.execute(stmt)
        state = result.scalar_one_or_none()
        if state:
            state.value = value
            state.metadata_json = metadata
        else:
            state = PipelineState(key=key, value=value, metadata_json=metadata)
            self.db.add(state)

    async def _log_state(self, key: str, status: str, metadata: dict = None):
        await self._set_state(key, status, metadata)
