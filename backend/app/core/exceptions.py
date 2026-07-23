"""
Custom Exceptions and Handlers
Standardized error responses
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger(__name__)


class NSMSException(Exception):
    """Base exception for NSMS"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(NSMSException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, "NOT_FOUND", details)


class UnauthorizedException(NSMSException):
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED", details)


class ForbiddenException(NSMSException):
    def __init__(self, message: str = "Forbidden - Insufficient permissions", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, "FORBIDDEN", details)


class BadRequestException(NSMSException):
    def __init__(self, message: str = "Bad request", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, "BAD_REQUEST", details)


class ConflictException(NSMSException):
    def __init__(self, message: str = "Conflict - Resource already exists", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, "CONFLICT", details)


class ValidationException(NSMSException):
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR", details)


async def nsms_exception_handler(request: Request, exc: NSMSException) -> JSONResponse:
    """Handle custom NSMS exceptions"""
    logger.warning(
        "nsms_exception",
        error_code=exc.error_code,
        status_code=exc.status_code,
        message=exc.message,
        path=str(request.url.path),
        method=request.method,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
            "timestamp": time.time(),
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors: List[Dict[str, Any]] = []
    for err in exc.errors():
        errors.append({
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "type": err.get("type"),
        })
    
    logger.warning("validation_error", errors=errors, path=str(request.url.path))
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {"errors": errors},
            },
            "timestamp": time.time(),
            "path": str(request.url.path),
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    logger.warning("http_exception", status_code=exc.status_code, detail=exc.detail, path=str(request.url.path))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "details": {},
            },
            "timestamp": time.time(),
            "path": str(request.url.path),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions"""
    logger.error("unhandled_exception", error=str(exc), path=str(request.url.path), exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": {} if not request.app.debug else {"error": str(exc)},
            },
            "timestamp": time.time(),
            "path": str(request.url.path),
        },
    )
