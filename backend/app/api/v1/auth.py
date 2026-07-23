"""
Auth API - Google OAuth + JWT
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.schemas.auth import GoogleAuthRequest, RefreshTokenRequest, TokenResponse, UserInfo
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user, get_current_active_user
from app.models.user import User
from app.constants.roles import ROLE_PERMISSIONS

router = APIRouter()
settings = get_settings()


@router.post("/google", response_model=dict, summary="Google OAuth Login")
async def google_login(
    payload: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate with Google ID token.
    Frontend obtains ID token via Google OAuth SDK and sends it here.
    Returns access + refresh tokens + user info.
    """
    auth_service = AuthService(db)
    result = await auth_service.authenticate_google(payload.id_token)
    
    user = result["user"]
    tokens = result["tokens"]
    permissions = result["permissions"]
    
    # Optionally set httpOnly cookies for refresh token
    # response.set_cookie(
    #     key="refresh_token",
    #     value=tokens["refresh_token"],
    #     httponly=True,
    #     secure=not settings.DEBUG,
    #     samesite="lax",
    #     max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    # )
    
    user_info = UserInfo(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        is_active=user.is_active,
        office_id=user.office_id,
        employee_id=user.employee_id,
        permissions=permissions,
    )
    
    return {
        "success": True,
        "data": {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_info.model_dump(),
        },
        "message": "Login successful",
    }


@router.post("/refresh", response_model=dict, summary="Refresh Access Token")
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    result = await auth_service.refresh_tokens(payload.refresh_token)
    
    user = result["user"]
    permissions = [p.value for p in ROLE_PERMISSIONS.get(user.role, [])]
    
    user_info = UserInfo(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        is_active=user.is_active,
        office_id=user.office_id,
        employee_id=user.employee_id,
        permissions=permissions,
    )
    
    return {
        "success": True,
        "data": {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_info.model_dump(),
        },
    }


@router.get("/me", response_model=dict, summary="Get Current User")
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Get current authenticated user profile"""
    
    permissions = [p.value for p in ROLE_PERMISSIONS.get(current_user.role, [])]
    
    user_info = UserInfo(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        is_active=current_user.is_active,
        office_id=current_user.office_id,
        employee_id=current_user.employee_id,
        permissions=permissions,
    )
    
    return {"success": True, "data": user_info.model_dump()}


@router.post("/logout", summary="Logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """Logout - client should discard tokens. Server could blacklist in future with Redis."""
    return {
        "success": True,
        "message": "Logged out successfully. Please discard tokens on client.",
    }


@router.get("/google/url", summary="Get Google OAuth URL")
async def get_google_oauth_url():
    """Get Google OAuth URL for redirect flow (alternative to ID token flow)"""
    from app.integrations.google_oauth import get_google_auth_url
    
    if not settings.GOOGLE_CLIENT_ID:
        return {
            "success": False,
            "message": "Google OAuth not configured",
            "configured": False,
        }
    
    url = get_google_auth_url(state="nsms-login")
    
    return {
        "success": True,
        "data": {"auth_url": url, "client_id": settings.GOOGLE_CLIENT_ID},
    }
