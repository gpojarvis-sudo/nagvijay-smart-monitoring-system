"""
Target schemas
"""
from __future__ import annotations

from typing import Optional, List, Dict
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.constants.status import TargetStatus, SchemeType, AchievementSource


class SchemeCreate(BaseModel):
    scheme_code: str = Field(..., min_length=2, max_length=50)
    scheme_name: str = Field(..., min_length=2, max_length=255)
    scheme_type: SchemeType
    description: Optional[str] = None
    financial_year: str = Field(..., pattern=r"^\d{4}-\d{2}$", example="2024-25")
    is_active: bool = True
    unit: str = Field(default="Count")
    metadata_json: Optional[Dict] = None


class SchemeUpdate(BaseModel):
    scheme_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    unit: Optional[str] = None
    metadata_json: Optional[Dict] = None


class SchemeResponse(BaseModel):
    id: str
    scheme_code: str
    scheme_name: str
    scheme_type: SchemeType
    description: Optional[str] = None
    financial_year: str
    is_active: bool
    unit: str
    metadata_json: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TargetCreate(BaseModel):
    scheme_id: str
    financial_year: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    division: str = Field(default="Nagpur City")
    region: str = Field(default="Nagpur")
    total_target: float = Field(..., gt=0)
    period_type: str = Field(default="YEARLY", pattern="^(DAILY|MONTHLY|QUARTERLY|YEARLY)$")
    start_date: date
    end_date: date


class TargetUpdate(BaseModel):
    total_target: Optional[float] = Field(default=None, gt=0)
    status: Optional[TargetStatus] = None
    end_date: Optional[date] = None


class TargetResponse(BaseModel):
    id: str
    scheme_id: str
    financial_year: str
    division: str
    region: str
    total_target: float
    period_type: str
    start_date: date
    end_date: date
    status: TargetStatus
    total_achieved: float
    achievement_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AllocationCreate(BaseModel):
    target_id: str
    scheme_id: str
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    allocated_target: float = Field(..., gt=0)
    financial_year: str
    month: Optional[int] = Field(default=None, ge=1, le=12)
    quarter: Optional[int] = Field(default=None, ge=1, le=4)


class AllocationResponse(BaseModel):
    id: str
    target_id: str
    scheme_id: str
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    allocated_target: float
    achieved: float
    achievement_percentage: float
    financial_year: str
    month: Optional[int] = None
    quarter: Optional[int] = None
    status: TargetStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AchievementCreate(BaseModel):
    allocation_id: str
    target_id: str
    scheme_id: str
    office_id: str
    employee_id: Optional[str] = None
    achievement_date: date
    amount: float = Field(..., gt=0)
    count: int = Field(default=1, ge=1)
    source: AchievementSource = AchievementSource.MANUAL
    source_id: Optional[str] = None
    remarks: Optional[str] = None
    additional_data: Optional[Dict] = None


class AchievementResponse(BaseModel):
    id: str
    allocation_id: str
    target_id: str
    scheme_id: str
    office_id: str
    employee_id: Optional[str] = None
    achievement_date: date
    amount: float
    count: int
    source: AchievementSource
    remarks: Optional[str] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BulkAllocationRequest(BaseModel):
    target_id: str
    financial_year: str
    allocations: List[AllocationCreate]
