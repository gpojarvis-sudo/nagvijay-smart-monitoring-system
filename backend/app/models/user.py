"""
User model - Authentication and RBAC
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.constants.roles import UserRole


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Auth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # For fallback
    
    # RBAC
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Office mapping
    office_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Metadata
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
