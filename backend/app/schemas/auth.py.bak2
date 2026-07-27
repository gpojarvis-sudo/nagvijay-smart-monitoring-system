"""
Auth schemas
"""
from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Google ID token from frontend")
    access_token: Optional[str] = Field(default=None, description="Optional Google access token")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")
    user: "UserInfo"


class UserInfo(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    office_id: Optional[str] = None
    employee_id: Optional[str] = None
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    success: bool = True
    data: TokenResponse
    message: str = "Login successful"


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
