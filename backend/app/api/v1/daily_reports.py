from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.daily_office_report_service import DailyOfficeReportService
from app.services.excel_export_service import ExcelExportService
from app.schemas.daily_report import DailyReportCreate, DailyReportResponse, DailyReportSummary
from app.integrations.google_sheets import get_sheets_client
from app.core.config import get_settings
from app.core.logging import get_logger
import io
import csv
import json

router = APIRouter(tags=["Daily Reports"])
logger = get_logger(__name__)

@router.get("/", response_model=List[DailyReportResponse])
async def get_daily_reports(
    report_date: Optional[date] = Query(default=None, description="Filter by date (YYYY-MM-DD)"),
    office_id: Optional[str] = Query(default=None),
    division: Optional[str] = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    reports = await service.get_reports(
        report_date=report_date,
        office_id=office_id,
        division=division,
    )
    return reports



@router.post("/", response_model=DailyReportResponse)
async def create_daily_report(
    payload: DailyReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    report = await service.upsert(payload.model_dump())

    # Append to Google Sheet (non-blocking: failure here must NOT roll back Supabase save)
    try:
        spreadsheet_id = get_settings().GOOGLE_SHEETS_SPREADSHEET_ID
        if spreadsheet_id:
            sheets_client = get_sheets_client()
            if sheets_client.is_configured():
                row = [
                    str(report.report_date),
                    report.office_id,
                    report.office_name,
                    report.office_code or "",
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
                await sheets_client.append_row(
                    spreadsheet_id=spreadsheet_id,
                    range_name="Sheet1!A1",
                    values=row,
                )
                logger.info("daily_report_sheet_append_success", report_id=report.id)
            else:
                logger.warning("daily_report_sheet_not_configured", report_id=report.id)
    except Exception as e:
        logger.error("daily_report_sheet_append_failed", report_id=report.id, error=str(e))

    return report


@router.get("/summary", response_model=DailyReportSummary)
async def get_daily_summary(
    report_date: date = Query(..., description="Date in YYYY-MM-DD"),
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    summary = await service.get_summary(report_date=report_date, division=division)
    return summary

@router.get("/export", summary="Export Daily Report")
async def export_daily_report(
    report_date: date = Query(..., description="Date in YYYY-MM-DD"),
    format: str = Query(default="csv", pattern="^(csv|json|excel)$"),
    office_id: Optional[str] = Query(default=None),
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    reports = await service.get_reports(
        report_date=report_date,
        office_id=office_id,
        division=division,
    )
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        if reports:
            headers = list(reports[0].__dict__.keys())
            headers = [h for h in headers if not h.startswith('_')]
            writer.writerow(headers)
            for r in reports:
                row = [getattr(r, h) for h in headers]
                writer.writerow(row)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=daily_report_{report_date.isoformat()}.csv"}
        )
    
    elif format == "json":
        data = []
        for r in reports:
            data.append({c.name: getattr(r, c.name) for c in r.__table__.columns})
        return Response(
            content=json.dumps(data, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=daily_report_{report_date.isoformat()}.json"}
        )
    
    elif format == "excel":
        try:
            output = ExcelExportService().generate(
                reports=reports,
                report_date=report_date,
            )

            return Response(
                content=output.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition":
                    f'attachment; filename="Daily_Monitoring_{report_date.isoformat()}.xlsx"'
                },
            )
        except Exception as e:
            import traceback
            return {
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

@router.get("/non-reporting", summary="Non-Reporting Offices for a Date")
async def get_non_reporting_offices(
    report_date: date = Query(..., description="Date in YYYY-MM-DD"),
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    offices = await service.get_non_reporting_offices(report_date=report_date, division=division)
    return {"report_date": report_date.isoformat(), "non_reporting_offices": offices}

@router.get("/{report_id}", response_model=DailyReportResponse)
async def get_daily_report_by_id(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    report = await service.get_by_id(report_id)
    return report
