"""
Common schemas - Pagination, Responses
"""
from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar
from datetime import datetime

from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(default=None, description="Search term")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    pagination: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        return cls(
            data=items,
            pagination={
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "has_next": page * page_size < total,
                "has_prev": page > 1,
            }
        )


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
    checks: dict
    uptime_seconds: float
