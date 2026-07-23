"""
User schemas
"""
from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.constants.roles import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.EMPLOYEE
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    office_id: Optional[str] = None
    
    class Config:
        from_attributes = True
