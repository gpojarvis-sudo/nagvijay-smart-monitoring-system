"""
Employee model - India Post employee master
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, DateTime, Date, Enum as SAEnum, func, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.constants.status import EmployeeStatus, EmployeeCategory, Designation


class Employee(Base):
    __tablename__ = "employees"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)  # e.g., EMP-NG-001
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Personal
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    category: Mapped[EmployeeCategory] = mapped_column(SAEnum(EmployeeCategory), default=EmployeeCategory.GENERAL)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Professional
    designation: Mapped[Designation] = mapped_column(SAEnum(Designation), nullable=False)
    office_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    reporting_manager_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Employment
    date_of_joining: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_of_retirement: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[EmployeeStatus] = mapped_column(SAEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
    is_gds: Mapped[bool] = mapped_column(Boolean, default=False)  # Gramin Dak Sevak
    
    # Transfer / Deputation
    previous_office_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    transfer_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # [{"from": "id", "to": "id", "date": "..."}]
    
    # Performance
    performance_score: Mapped[Optional[float]] = mapped_column(default=0.0)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Employee {self.employee_code}: {self.full_name}>"
