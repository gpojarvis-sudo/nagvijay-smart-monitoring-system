"""
Office model - Post Office master
Supports HO, SO, BO hierarchy for India Post
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SAEnum, func, Float, Integer, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.constants.status import OfficeType, OfficeStatus


class Office(Base):
    __tablename__ = "offices"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    office_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)  # e.g., NG-123
    office_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Hierarchy
    office_type: Mapped[OfficeType] = mapped_column(SAEnum(OfficeType), nullable=False)
    parent_office_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)  # For SO->HO, BO->SO
    division: Mapped[str] = mapped_column(String(100), nullable=False, index=True, default="Nagpur City")
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="Nagpur")
    circle: Mapped[str] = mapped_column(String(100), nullable=False, default="Maharashtra")
    
    # Location
    pincode: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    taluka: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Contact
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Beat / Jurisdiction
    beat_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    jurisdiction_area: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Operational
    status: Mapped[OfficeStatus] = mapped_column(SAEnum(OfficeStatus), default=OfficeStatus.ACTIVE, nullable=False)
    is_delivery_office: Mapped[bool] = mapped_column(Boolean, default=True)
    working_hours: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"mon_fri": "10-5", "sat": "10-2"}
    
    # Stats (denormalized for performance)
    total_employees: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Office {self.office_code}: {self.office_name}>"
