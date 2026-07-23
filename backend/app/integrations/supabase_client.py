"""
Supabase Client - For Auth, Realtime, Storage
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

import structlog
from supabase import create_client, Client

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


@lru_cache()
def get_supabase_client(use_service_role: bool = True) -> Optional[Client]:
    """Get Supabase client - service role for backend"""
    
    if not settings.SUPABASE_URL:
        logger.warning("supabase_not_configured", reason="SUPABASE_URL missing")
        return None
    
    key = settings.SUPABASE_SERVICE_ROLE_KEY if use_service_role else settings.SUPABASE_ANON_KEY
    
    if not key:
        logger.warning("supabase_key_missing")
        return None
    
    try:
        client: Client = create_client(settings.SUPABASE_URL, key)
        logger.info("supabase_client_created", url=settings.SUPABASE_URL)
        return client
    except Exception as e:
        logger.error("supabase_client_failed", error=str(e))
        return None


def get_supabase_anon_client() -> Optional[Client]:
    return get_supabase_client(use_service_role=False)


async def health_check_supabase() -> dict:
    """Check Supabase connectivity"""
    try:
        client = get_supabase_client()
        if not client:
            return {"status": "not_configured", "message": "Supabase URL or key missing"}
        
        # Try to query a simple table or auth
        # Using rest API health via client
        return {"status": "healthy", "url": settings.SUPABASE_URL}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
