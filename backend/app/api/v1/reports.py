"""
Reports API
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.analytics import ReportRequest, AnalyticsFilter
from app.services.report_service import ReportService

router = APIRouter()


@router.post("/generate", response_model=dict, summary="Generate Report")
async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = ReportService(db)
    report = await service.generate_report(request)
    return {"success": True, "data": report}


@router.get("/dpr", response_model=dict, summary="Daily Performance Report")
async def get_dpr(
    division: str = Query(default="Nagpur City"),
    report_date: Optional[str] = Query(default=None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = ReportService(db)
    report = await service.get_dpr(division=division, report_date=report_date)
    return {"success": True, "data": report}


@router.get("/monthly", response_model=dict, summary="Monthly Consolidated Report")
async def get_monthly_report(
    financial_year: str = Query(..., pattern=r"^\d{4}-\d{2}$", example="2024-25"),
    month: int = Query(..., ge=1, le=12),
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = ReportService(db)
    report = await service.get_monthly_consolidated(financial_year=financial_year, month=month, division=division)
    return {"success": True, "data": report}


@router.get("/export", response_model=dict, summary="Export Report")
async def export_report(
    report_type: str = Query(..., pattern="^(DAILY|MONTHLY|OFFICE_WISE|SCHEME_WISE)$"),
    format: str = Query(default="JSON", pattern="^(JSON|PDF|EXCEL|CSV)$"),
    financial_year: Optional[str] = Query(default=None),
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = AnalyticsFilter(financial_year=financial_year, division=division)
    request = ReportRequest(report_type=report_type, filters=filters, format=format)
    
    service = ReportService(db)
    report = await service.generate_report(request)
    
    return {
        "success": True,
        "data": report,
        "message": f"Report {report_type} generated in {format} format",
    }
