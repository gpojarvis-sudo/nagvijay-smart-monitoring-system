"""
Logging Middleware - Request/Response logging with context
"""
from __future__ import annotations

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Bind context for structlog
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            client_ip=request.client.host if request.client else "unknown",
        )
        
        start_time = time.time()
        
        # Log request
        logger.info(
            "request_started",
            query_params=str(request.query_params),
            user_agent=request.headers.get("user-agent", "unknown"),
        )
        
        try:
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )
            
            # Add request ID header
            response.headers["X-Request-ID"] = request_id
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()
