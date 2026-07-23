"""
Analytics schemas
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from datetime import date, datetime

from pydantic import BaseModel, Field


class AnalyticsFilter(BaseModel):
    financial_year: Optional[str] = None
    division: Optional[str] = None
    region: Optional[str] = None
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    scheme_id: Optional[str] = None
    scheme_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    period_type: Optional[str] = None
    office_type: Optional[str] = None


class KPIData(BaseModel):
    total_offices: int
    total_employees: int
    total_targets: int
    total_achieved: float
    overall_achievement_percentage: float
    active_schemes: int
    pending_verifications: int


class ChartDataPoint(BaseModel):
    label: str
    value: float
    count: Optional[int] = None
    percentage: Optional[float] = None
    additional: Optional[Dict[str, Any]] = None


class TrendData(BaseModel):
    date: str
    target: float
    achieved: float
    percentage: float


class DashboardStats(BaseModel):
    kpis: KPIData
    achievement_trend: List[TrendData]
    scheme_wise: List[ChartDataPoint]
    office_wise: List[ChartDataPoint]
    top_performers: List[Dict[str, Any]]
    low_performers: List[Dict[str, Any]]
    recent_achievements: List[Dict[str, Any]]


class ReportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(DAILY|MONTHLY|QUARTERLY|YEARLY|OFFICE_WISE|EMPLOYEE_WISE|SCHEME_WISE)$")
    filters: AnalyticsFilter
    format: str = Field(default="JSON", pattern="^(JSON|PDF|EXCEL|CSV)$")
    include_charts: bool = True


class ReportResponse(BaseModel):
    id: str
    report_type: str
    generated_at: datetime
    filters: Dict[str, Any]
    data: Dict[str, Any]
    download_url: Optional[str] = None


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AIChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
