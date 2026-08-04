"""
Auth dependencies - JWT extraction and current user
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.services.auth_service import AuthService

security = HTTPBearer(auto_error=False)


async def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


async def get_token_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Extract and validate token payload"""
    if not credentials:
        return None
    
    try:
        payload = decode_token(credentials.credentials)
        return payload
    except ValueError:
        return None


async def get_current_user_optional(
    payload: Optional[Dict[str, Any]] = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, else None"""
    if not payload:
        return None
    
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(payload)
        return user
    except Exception:
        return None


async def get_current_user(
    payload: Optional[Dict[str, Any]] = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require authentication - raises 401 if not authenticated"""
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(payload)
        return user
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


async def get_current_user_with_payload(
    payload: Optional[Dict[str, Any]] = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db),
) -> tuple[User, Dict[str, Any]]:
    """Get user and raw payload (for permissions)"""
    
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(payload)
    return user, payload
