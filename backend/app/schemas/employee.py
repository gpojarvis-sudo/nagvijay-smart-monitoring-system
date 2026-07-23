"""
Employee schemas
"""
from __future__ import annotations

from typing import Optional, List, Dict
from datetime import date, datetime

from pydantic import BaseModel, Field, EmailStr

from app.constants.status import EmployeeStatus, EmployeeCategory, Designation


class EmployeeCreate(BaseModel):
    employee_code: str = Field(..., min_length=2, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(default=None, pattern="^(Male|Female|Other)$")
    category: EmployeeCategory = EmployeeCategory.GENERAL
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    designation: Designation
    office_id: str
    reporting_manager_id: Optional[str] = None
    date_of_joining: Optional[date] = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    is_gds: bool = False


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    category: Optional[EmployeeCategory] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    designation: Optional[Designation] = None
    office_id: Optional[str] = None
    reporting_manager_id: Optional[str] = None
    date_of_joining: Optional[date] = None
    date_of_retirement: Optional[date] = None
    status: Optional[EmployeeStatus] = None
    is_gds: Optional[bool] = None


class EmployeeResponse(BaseModel):
    id: str
    employee_code: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    category: EmployeeCategory
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    designation: Designation
    office_id: str
    reporting_manager_id: Optional[str] = None
    date_of_joining: Optional[date] = None
    date_of_retirement: Optional[date] = None
    status: EmployeeStatus
    is_gds: bool
    performance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeStats(BaseModel):
    total: int
    by_designation: Dict[str, int]
    by_status: Dict[str, int]
    by_office: Dict[str, int]
