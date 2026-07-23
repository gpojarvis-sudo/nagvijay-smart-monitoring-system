"""
Report Service - Generate reports in various formats
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional
import io
import json

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import AnalyticsFilter, ReportRequest
from app.services.analytics_service import AnalyticsService

logger = structlog.get_logger(__name__)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = AnalyticsService(db)
    
    async def generate_report(self, request: ReportRequest) -> Dict[str, Any]:
        """Generate report based on type and filters"""
        
        dashboard_stats = await self.analytics_service.get_dashboard_stats(request.filters)
        
        report_data = {
            "report_type": request.report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "filters": request.filters.model_dump(),
            "kpis": dashboard_stats.kpis.model_dump(),
            "scheme_wise": dashboard_stats.scheme_wise,
            "office_wise": dashboard_stats.office_wise,
            "top_performers": dashboard_stats.top_performers,
            "low_performers": dashboard_stats.low_performers,
        }
        
        # Add specific data based on report type
        if request.report_type == "DAILY":
            report_data["trend"] = dashboard_stats.achievement_trend
        elif request.report_type == "MONTHLY":
            report_data["trend"] = dashboard_stats.achievement_trend
            report_data["recent_achievements"] = dashboard_stats.recent_achievements
        
        # Generate format
        if request.format == "JSON":
            return report_data
        elif request.format == "CSV":
            # For CSV, return structured data that frontend can convert
            return report_data
        elif request.format == "EXCEL":
            # Return data for Excel generation (frontend or backend)
            return report_data
        elif request.format == "PDF":
            return report_data
        else:
            return report_data
    
    async def get_dpr(self, division: str = "Nagpur City", report_date: Optional[str] = None) -> Dict[str, Any]:
        """Daily Performance Report"""
        from datetime import date
        target_date = date.fromisoformat(report_date) if report_date else date.today()
        
        filters = AnalyticsFilter(
            division=division,
            start_date=target_date,
            end_date=target_date,
        )
        
        stats = await self.analytics_service.get_dashboard_stats(filters)
        
        return {
            "report_type": "DPR",
            "date": target_date.isoformat(),
            "division": division,
            "stats": stats.model_dump(),
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def get_monthly_consolidated(self, financial_year: str, month: int, division: str = "Nagpur City") -> Dict[str, Any]:
        """Monthly consolidated report"""
        filters = AnalyticsFilter(
            financial_year=financial_year,
            division=division,
        )
        
        stats = await self.analytics_service.get_dashboard_stats(filters)
        
        return {
            "report_type": "MONTHLY_CONSOLIDATED",
            "financial_year": financial_year,
            "month": month,
            "division": division,
            "stats": stats.model_dump(),
            "generated_at": datetime.utcnow().isoformat(),
        }
