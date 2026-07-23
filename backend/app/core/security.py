"""
Security - JWT, Password hashing, OAuth helpers
Production-ready with access + refresh tokens
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
import structlog
from passlib.context import CryptContext

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": settings.JWT_ISSUER,
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)
    
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create refresh token - longer expiry"""
    if expires_delta is None:
        expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": settings.JWT_ISSUER,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    }
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("token_expired")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning("invalid_token", error=str(e))
        raise ValueError(f"Invalid token: {str(e)}")


def create_tokens_pair(user_id: str, extra_claims: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """Create access + refresh pair"""
    access = create_access_token(subject=user_id, extra_claims=extra_claims)
    refresh = create_refresh_token(subject=user_id)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


def generate_secure_random_string(length: int = 32) -> str:
    """Generate secure random string for secrets"""
    import secrets
    return secrets.token_urlsafe(length)
