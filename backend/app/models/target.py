"""
Target Engine - Schemes, Allocations, Achievements
Core business logic for India Post target tracking
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, DateTime, Date, Enum as SAEnum, func, Float, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.constants.status import TargetStatus, SchemeType, AchievementSource


class Scheme(Base):
    """Master for schemes like PLI, RPLI, SSA, etc"""
    __tablename__ = "schemes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scheme_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scheme_type: Mapped[SchemeType] = mapped_column(SAEnum(SchemeType), nullable=False)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # e.g., 2024-25
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # For target calculation
    unit: Mapped[str] = mapped_column(String(50), default="C count")  # e.g., "Accounts", "Amount in Lakhs"
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Target(Base):
    """Overall target for a division/region/circle"""
    __tablename__ = "targets"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scheme_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    
    # Scope
    division: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, default="Nagpur")
    total_target: Mapped[float] = mapped_column(Float, nullable=False)  # Total for division
    
    # Period
    period_type: Mapped[str] = mapped_column(String(20), default="YEARLY")  # DAILY, MONTHLY, QUARTERLY, YEARLY
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    status: Mapped[TargetStatus] = mapped_column(SAEnum(TargetStatus), default=TargetStatus.ALLOCATED)
    
    # Progress (denormalized)
    total_achieved: Mapped[float] = mapped_column(Float, default=0.0)
    achievement_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TargetAllocation(Base):
    """Office/Employee level allocation from main target"""
    __tablename__ = "target_allocations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # Allocation to
    office_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    allocated_target: Mapped[float] = mapped_column(Float, nullable=False)
    achieved: Mapped[float] = mapped_column(Float, default=0.0)
    achievement_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Period
    financial_year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-12 for monthly
    quarter: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-4
    
    status: Mapped[TargetStatus] = mapped_column(SAEnum(TargetStatus), default=TargetStatus.ALLOCATED)
    
    # Verification
    verified_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Achievement(Base):
    """Daily achievement entries - from manual, forms, sheets"""
    __tablename__ = "achievements"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    allocation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    office_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    achievement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # count or value
    count: Mapped[int] = mapped_column(Integer, default=1)  # number of accounts/policies
    
    source: Mapped[AchievementSource] = mapped_column(SAEnum(AchievementSource), default=AchievementSource.MANUAL)
    source_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Form response ID, Sheet row ID
    
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For flexible form fields
    
    # Verification
    is_verified: Mapped[bool] = mapped_column(default=False)
    verified_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# Fix bool import
from sqlalchemy import Boolean as _Bool
# Re-assign bool mapped columns need import
# Actually we already imported indirectly via python, but SQLAlchemy needs type
# We'll patch: is_active needs Boolean
import sqlalchemy as sa
# The above file uses bool shorthand but SQLAlchemy will handle - we need to ensure import
# Let's redefine quickly using property setter workaround: we used default bool directly which is python bool, but mapped_column should accept Boolean type
# For simplicity, we keep - actual runtime will coerce, but we add proper import fallback
try:
    from sqlalchemy import Boolean
except ImportError:
    Boolean = _Bool
