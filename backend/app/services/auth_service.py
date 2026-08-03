"""
Auth Service - Google OAuth + JWT
Production-ready with Supabase fallback
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_tokens_pair,
    decode_token,
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import (
    UnauthorizedException,
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.constants.roles import UserRole, ROLE_PERMISSIONS
from app.schemas.auth import RegisterRequest, LoginRequest

logger = structlog.get_logger(__name__)
settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid refresh token type")
            
            user_id = payload.get("sub")
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                raise UnauthorizedException("User not found or inactive")
            
            permissions = [p.value for p in ROLE_PERMISSIONS.get(user.role, [])]
            extra_claims = {
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "permissions": permissions,
            }
            
            # Create new access token only (or both)
            access_token = create_access_token(subject=user.id, extra_claims=extra_claims)
            
            # For security, also rotate refresh token
            tokens = create_tokens_pair(user.id, extra_claims)
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": "bearer",
                "user": user,
            }
        
        except ValueError as e:
            raise UnauthorizedException(str(e))
    

    async def register(self, data: RegisterRequest) -> Dict[str, Any]:
        """Register with email and password"""
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictException("Email already registered")

        user = await self.user_repo.create({
            "email": data.email,
            "full_name": data.full_name,
            "hashed_password": hash_password(data.password),
            "role": UserRole.EMPLOYEE,
            "is_active": True,
            "is_verified": False,
        })

        permissions = [p.value for p in ROLE_PERMISSIONS.get(user.role, [])]

        extra_claims = {
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "permissions": permissions,
        }

        tokens = create_tokens_pair(user.id, extra_claims)

        return {
            "user": user,
            "tokens": tokens,
            "permissions": permissions,
        }


    async def login(self, data: LoginRequest) -> Dict[str, Any]:
        """Login with email and password"""
        user = await self.user_repo.get_by_username(data.username)

        if not user:
            raise UnauthorizedException("Invalid Employee ID or password")

        if not user.hashed_password:
            raise UnauthorizedException("Password login is not configured for this account.")

        if not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid Employee ID or password")

        if not user.is_active:
            raise UnauthorizedException("User account is deactivated")

        permissions = [p.value for p in ROLE_PERMISSIONS.get(user.role, [])]

        extra_claims = {
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "permissions": permissions,
        }

        tokens = create_tokens_pair(user.id, extra_claims)

        return {
            "user": user,
            "tokens": tokens,
            "permissions": permissions,
        }

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
    
    async def get_current_user(self, token_payload: Dict[str, Any]) -> User:
        user_id = token_payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        if not user.is_active:
            raise UnauthorizedException("User deactivated")
        
        return user
