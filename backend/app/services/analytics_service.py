"""
Analytics Service - Dashboard KPIs, Trends, Reports
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.office import Office
from app.models.employee import Employee
from app.models.target import Target, TargetAllocation, Achievement, Scheme
from app.schemas.analytics import AnalyticsFilter, KPIData, DashboardStats

logger = structlog.get_logger(__name__)


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_stats(self, filters: Optional[AnalyticsFilter] = None) -> DashboardStats:
        filters = filters or AnalyticsFilter()
        
        # KPI counts
        total_offices = await self._count_offices(filters)
        total_employees = await self._count_employees(filters)
        
        # Targets
        target_query = select(func.count(), func.coalesce(func.sum(Target.total_target), 0), func.coalesce(func.sum(Target.total_achieved), 0)).select_from(Target)
        if filters.financial_year:
            target_query = target_query.where(Target.financial_year == filters.financial_year)
        if filters.division:
            target_query = target_query.where(Target.division == filters.division)
        target_result = await self.db.execute(target_query)
        target_row = target_result.first()
        total_targets_count = target_row[0] if target_row else 0
        total_target_sum = float(target_row[1] if target_row else 0)
        total_achieved_sum = float(target_row[2] if target_row else 0)
        
        overall_perc = (total_achieved_sum / total_target_sum * 100) if total_target_sum > 0 else 0
        
        # Active schemes
        scheme_query = select(func.count()).select_from(Scheme).where(Scheme.is_active == True)
        if filters.financial_year:
            scheme_query = scheme_query.where(Scheme.financial_year == filters.financial_year)
        scheme_result = await self.db.execute(scheme_query)
        active_schemes = scheme_result.scalar() or 0
        
        # Pending verifications
        pending_result = await self.db.execute(select(func.count()).select_from(Achievement).where(Achievement.is_verified == False))
        pending = pending_result.scalar() or 0
        
        kpis = KPIData(
            total_offices=total_offices,
            total_employees=total_employees,
            total_targets=total_targets_count,
            total_achieved=total_achieved_sum,
            overall_achievement_percentage=round(overall_perc, 2),
            active_schemes=active_schemes,
            pending_verifications=pending,
        )
        
        # Trends - last 30 days
        achievement_trend = await self._get_achievement_trend(filters)
        
        # Scheme wise breakdown
        scheme_wise = await self._get_scheme_wise(filters)
        
        # Office wise
        office_wise = await self._get_office_wise(filters)
        
        # Top performers
        top_performers = await self._get_top_performers(filters)
        low_performers = await self._get_low_performers(filters)
        
        # Recent achievements
        recent_achievements = await self._get_recent_achievements(filters)
        
        return DashboardStats(
            kpis=kpis,
            achievement_trend=achievement_trend,
            scheme_wise=scheme_wise,
            office_wise=office_wise,
            top_performers=top_performers,
            low_performers=low_performers,
            recent_achievements=recent_achievements,
        )
    
    async def _count_offices(self, filters: AnalyticsFilter) -> int:
        query = select(func.count()).select_from(Office)
        if filters.division:
            query = query.where(Office.division == filters.division)
        if filters.office_type:
            query = query.where(Office.office_type == filters.office_type)
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_employees(self, filters: AnalyticsFilter) -> int:
        query = select(func.count()).select_from(Employee)
        if filters.office_id:
            query = query.where(Employee.office_id == filters.office_id)
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_achievement_trend(self, filters: AnalyticsFilter) -> List[Dict]:
        # Last 30 days daily achievements
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        query = (
            select(
                Achievement.achievement_date,
                func.coalesce(func.sum(Achievement.amount), 0).label("total"),
                func.count().label("cnt")
            )
            .where(and_(Achievement.achievement_date >= start_date, Achievement.achievement_date <= end_date))
            .group_by(Achievement.achievement_date)
            .order_by(Achievement.achievement_date.asc())
        )
        
        if filters.office_id:
            query = query.where(Achievement.office_id == filters.office_id)
        if filters.scheme_id:
            query = query.where(Achievement.scheme_id == filters.scheme_id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        trend = []
        for row in rows:
            trend.append({
                "date": row[0].isoformat(),
                "achieved": float(row[1]),
                "target": 0,  # Would need target per day - simplified
                "percentage": 0,
                "count": row[2],
            })
        return trend
    
    async def _get_scheme_wise(self, filters: AnalyticsFilter) -> List[Dict]:
        # Sum achievement per scheme
        query = (
            select(
                Scheme.scheme_name,
                Scheme.scheme_type,
                func.coalesce(func.sum(Achievement.amount), 0).label("achieved"),
                func.count(Achievement.id).label("cnt")
            )
            .join(Achievement, Achievement.scheme_id == Scheme.id)
            .group_by(Scheme.scheme_name, Scheme.scheme_type)
        )
        
        if filters.financial_year:
            query = query.where(Scheme.financial_year == filters.financial_year)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        data = []
        for row in rows:
            data.append({
                "label": row[0],
                "value": float(row[2]),
                "count": row[3],
                "additional": {"type": str(row[1])}
            })
        return data
    
    async def _get_office_wise(self, filters: AnalyticsFilter) -> List[Dict]:
        query = (
            select(
                Office.office_name,
                Office.office_code,
                func.coalesce(func.sum(Achievement.amount), 0).label("achieved"),
                func.coalesce(func.sum(TargetAllocation.allocated_target), 0).label("target")
            )
            .join(Achievement, Achievement.office_id == Office.id, isouter=True)
            .join(TargetAllocation, TargetAllocation.office_id == Office.id, isouter=True)
            .group_by(Office.office_name, Office.office_code)
            .limit(20)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        data = []
        for row in rows:
            target_val = float(row[3] or 0)
            achieved_val = float(row[2] or 0)
            perc = (achieved_val / target_val * 100) if target_val > 0 else 0
            data.append({
                "label": f"{row[1]} - {row[0]}",
                "value": achieved_val,
                "percentage": round(perc, 2),
            })
        return data
    
    async def _get_top_performers(self, filters: AnalyticsFilter, limit: int = 5) -> List[Dict]:
        query = (
            select(
                TargetAllocation.office_id,
                Office.office_name,
                Office.office_code,
                TargetAllocation.achieved,
                TargetAllocation.allocated_target,
                TargetAllocation.achievement_percentage
            )
            .join(Office, Office.id == TargetAllocation.office_id, isouter=True)
            .order_by(TargetAllocation.achievement_percentage.desc())
            .limit(limit)
        )
        
        if filters.financial_year:
            query = query.where(TargetAllocation.financial_year == filters.financial_year)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        performers = []
        for row in rows:
            performers.append({
                "office_id": row[0],
                "office_name": row[1],
                "office_code": row[2],
                "achieved": float(row[3]),
                "target": float(row[4]),
                "percentage": float(row[5]),
            })
        return performers
    
    async def _get_low_performers(self, filters: AnalyticsFilter, limit: int = 5) -> List[Dict]:
        query = (
            select(
                TargetAllocation.office_id,
                Office.office_name,
                Office.office_code,
                TargetAllocation.achieved,
                TargetAllocation.allocated_target,
                TargetAllocation.achievement_percentage
            )
            .join(Office, Office.id == TargetAllocation.office_id, isouter=True)
            .order_by(TargetAllocation.achievement_percentage.asc())
            .limit(limit)
        )
        
        if filters.financial_year:
            query = query.where(TargetAllocation.financial_year == filters.financial_year)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        performers = []
        for row in rows:
            performers.append({
                "office_id": row[0],
                "office_name": row[1],
                "office_code": row[2],
                "achieved": float(row[3]),
                "target": float(row[4]),
                "percentage": float(row[5]),
            })
        return performers
    
    async def _get_recent_achievements(self, filters: AnalyticsFilter, limit: int = 10) -> List[Dict]:
        query = (
            select(Achievement, Office.office_name, Scheme.scheme_name)
            .join(Office, Office.id == Achievement.office_id, isouter=True)
            .join(Scheme, Scheme.id == Achievement.scheme_id, isouter=True)
            .order_by(Achievement.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        achievements = []
        for row in rows:
            ach = row[0]
            achievements.append({
                "id": ach.id,
                "office_name": row[1],
                "scheme_name": row[2],
                "amount": float(ach.amount),
                "date": ach.achievement_date.isoformat(),
                "source": str(ach.source),
                "is_verified": ach.is_verified,
            })
        return achievements
