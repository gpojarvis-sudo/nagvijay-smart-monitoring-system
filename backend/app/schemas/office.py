"""
Office schemas
"""
from __future__ import annotations

from typing import Optional, Dict, List
from datetime import datetime

from pydantic import BaseModel, Field

from app.constants.status import OfficeType, OfficeStatus


class OfficeCreate(BaseModel):
    office_code: str = Field(..., min_length=2, max_length=20, description="Unique office code")
    office_name: str = Field(..., min_length=2, max_length=255)
    office_type: OfficeType
    parent_office_id: Optional[str] = None
    division: str = Field(default="Nagpur City")
    region: str = Field(default="Nagpur")
    circle: str = Field(default="Maharashtra")
    pincode: str = Field(..., min_length=6, max_length=10)
    district: str = Field(...)
    taluka: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    phone: Optional[str] = None
    email: Optional[str] = None
    beat_number: Optional[str] = None
    jurisdiction_area: Optional[str] = None
    status: OfficeStatus = OfficeStatus.ACTIVE
    is_delivery_office: bool = True
    working_hours: Optional[Dict] = None


class OfficeUpdate(BaseModel):
    office_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    office_type: Optional[OfficeType] = None
    parent_office_id: Optional[str] = None
    division: Optional[str] = None
    region: Optional[str] = None
    circle: Optional[str] = None
    pincode: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    beat_number: Optional[str] = None
    jurisdiction_area: Optional[str] = None
    status: Optional[OfficeStatus] = None
    is_delivery_office: Optional[bool] = None
    working_hours: Optional[Dict] = None


class OfficeResponse(BaseModel):
    id: str
    office_code: str
    office_name: str
    office_type: OfficeType
    parent_office_id: Optional[str] = None
    division: str
    region: str
    circle: str
    pincode: str
    district: str
    taluka: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    beat_number: Optional[str] = None
    jurisdiction_area: Optional[str] = None
    status: OfficeStatus
    is_delivery_office: bool
    working_hours: Optional[Dict] = None
    total_employees: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OfficeBulkImport(BaseModel):
    offices: List[OfficeCreate]


class OfficeStats(BaseModel):
    total_offices: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_division: Dict[str, int]
