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
from app.core.security import create_tokens_pair, decode_token, create_access_token
from app.core.exceptions import UnauthorizedException, BadRequestException, NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.integrations.google_oauth import verify_google_token, get_google_user_info
from app.constants.roles import UserRole, ROLE_PERMISSIONS

logger = structlog.get_logger(__name__)
settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def authenticate_google(self, id_token: str) -> Dict[str, Any]:
        """Authenticate with Google ID token"""
        try:
            google_user = await verify_google_token(id_token)
            if not google_user:
                raise UnauthorizedException("Invalid Google token")
            
            email = google_user.get("email")
            if not email:
                raise BadRequestException("Email not found in Google token")
            
            # Check domain restriction if needed (for India Post - allow all for MVP)
            # if not email.endswith("@indiapost.gov.in") and not email.endswith("@gmail.com"):
            #     raise ForbiddenException("Only India Post domain allowed")
            
            # Find or create user
            user = await self.user_repo.get_by_email(email)
            
            if not user:
                # Auto-create user for MVP - In production, might need admin approval
                user_data = {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "full_name": google_user.get("name", email.split("@")[0]),
                    "avatar_url": google_user.get("picture"),
                    "google_id": google_user.get("sub"),
                    "role": UserRole.EMPLOYEE,
                    "is_active": True,
                    "is_verified": google_user.get("email_verified", False),
                    "last_login_at": datetime.now(timezone.utc),
                }
                user = await self.user_repo.create(user_data)
                logger.info("new_user_created_via_google", email=email, user_id=user.id)
            else:
                # Update last login and google_id if missing
                update_data = {"last_login_at": datetime.now(timezone.utc)}
                if not user.google_id:
                    update_data["google_id"] = google_user.get("sub")
                if not user.avatar_url and google_user.get("picture"):
                    update_data["avatar_url"] = google_user.get("picture")
                user = await self.user_repo.update(user.id, update_data)
                
                if not user.is_active:
                    raise UnauthorizedException("User account is deactivated")
            
            # Create tokens
            permissions = [p.value for p in ROLE_PERMISSIONS.get(user.role, [])]
            extra_claims = {
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "permissions": permissions,
            }
            
            tokens = create_tokens_pair(user.id, extra_claims)
            
            return {
                "user": user,
                "tokens": tokens,
                "permissions": permissions,
            }
        
        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error("google_auth_failed", error=str(e))
            raise UnauthorizedException(f"Google authentication failed: {str(e)}")
    
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
