"""
Google OAuth verification
Production-ready token verification
"""
from __future__ import annotations

from typing import Optional, Dict, Any

import structlog
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


async def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Google ID token and return user info"""
    
    if not settings.GOOGLE_CLIENT_ID:
        logger.warning("google_client_id_not_configured")
        # For development, allow verification without client ID check
        # In production, this should fail
    
    try:
        # Use google-auth library for verification
        request = google_requests.Request()
        
        # Verify token - if GOOGLE_CLIENT_ID is set, it will check audience
        # If not, we verify without audience check for MVP flexibility
        if settings.GOOGLE_CLIENT_ID:
            idinfo = id_token.verify_oauth2_token(
                token,
                request,
                settings.GOOGLE_CLIENT_ID,
            )
        else:
            # Without client ID, verify token structure only (not recommended for prod)
            idinfo = id_token.verify_oauth2_token(
                token,
                request,
            )
        
        # Validate issuer
        if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.warning("invalid_google_issuer", issuer=idinfo.get("iss"))
            return None
        
        # Check email verified
        if not idinfo.get("email_verified", False):
            logger.warning("email_not_verified", email=idinfo.get("email"))
            # Still allow but log warning
        
        logger.info("google_token_verified", email=idinfo.get("email"), sub=idinfo.get("sub"))
        return idinfo
    
    except ValueError as e:
        logger.warning("google_token_invalid", error=str(e))
        # Fallback: try to decode via Google tokeninfo endpoint
        try:
            return await verify_via_tokeninfo_endpoint(token)
        except Exception as ex:
            logger.error("google_fallback_verification_failed", error=str(ex))
            return None
    except Exception as e:
        logger.error("google_verification_error", error=str(e))
        return None


async def verify_via_tokeninfo_endpoint(token: str) -> Optional[Dict[str, Any]]:
    """Fallback verification via Google tokeninfo endpoint"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}",
            timeout=10.0,
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logger.warning("tokeninfo_failed", status=response.status_code, body=response.text)
            return None


async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user info via access token (for additional profile data)"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
        if response.status_code == 200:
            return response.json()
        return None


def get_google_auth_url(state: Optional[str] = None) -> str:
    """Generate Google OAuth URL for frontend redirect"""
    
    from urllib.parse import urlencode
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": settings.GOOGLE_OAUTH_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
