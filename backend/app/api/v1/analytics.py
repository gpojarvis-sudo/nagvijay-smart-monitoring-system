"""
Analytics API - Dashboard KPIs and analytics
"""
from __future__ import annotations

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.analytics import AnalyticsFilter
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=dict, summary="Get Dashboard Stats")
async def get_dashboard_stats(
    financial_year: Optional[str] = Query(default=None),
    division: Optional[str] = Query(default="Nagpur City"),
    region: Optional[str] = Query(default=None),
    office_id: Optional[str] = Query(default=None),
    scheme_id: Optional[str] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = AnalyticsFilter(
        financial_year=financial_year,
        division=division,
        region=region,
        office_id=office_id,
        scheme_id=scheme_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    service = AnalyticsService(db)
    stats = await service.get_dashboard_stats(filters)
    
    return {"success": True, "data": stats.model_dump()}


@router.get("/kpis", response_model=dict, summary="Get KPIs Only")
async def get_kpis(
    financial_year: Optional[str] = Query(default=None),
    division: Optional[str] = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = AnalyticsFilter(financial_year=financial_year, division=division)
    service = AnalyticsService(db)
    stats = await service.get_dashboard_stats(filters)
    return {"success": True, "data": stats.kpis.model_dump()}


@router.get("/trends", response_model=dict, summary="Get Achievement Trends")
async def get_trends(
    financial_year: Optional[str] = Query(default=None),
    office_id: Optional[str] = Query(default=None),
    scheme_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = AnalyticsFilter(financial_year=financial_year, office_id=office_id, scheme_id=scheme_id)
    service = AnalyticsService(db)
    stats = await service.get_dashboard_stats(filters)
    return {"success": True, "data": {"trend": stats.achievement_trend}}
