from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.daily_office_report_service import DailyOfficeReportService
from app.schemas.daily_report import DailyReportResponse, DailyReportSummary

router = APIRouter(prefix="/daily-reports", tags=["Daily Reports"])

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

@router.get("/{report_id}", response_model=DailyReportResponse)
async def get_daily_report_by_id(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    report = await service.get_by_id(report_id)
    return report
