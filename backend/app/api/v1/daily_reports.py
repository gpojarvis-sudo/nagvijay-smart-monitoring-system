from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.daily_office_report_service import DailyOfficeReportService
from app.schemas.daily_report import DailyReportResponse, DailyReportSummary
import io
import csv
import json

router = APIRouter(tags=["Daily Reports"])

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
    format: str = Query(default="csv", regex="^(csv|json)$"),
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
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Report"
        if reports:
            headers = list(reports[0].__dict__.keys())
            headers = [h for h in headers if not h.startswith('_')]
            ws.append(headers)
            for r in reports:
                row = [getattr(r, h) for h in headers]
                ws.append(row)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=daily_report_{report_date.isoformat()}.xlsx"}
        )

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
