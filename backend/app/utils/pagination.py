"""
Pagination utilities
"""
from __future__ import annotations

from typing import Generic, TypeVar, List, Optional
from dataclasses import dataclass

from pydantic import BaseModel

T = TypeVar("T")


@dataclass
class PaginationResult(Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        return self.page * self.page_size < self.total
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


def paginate(total: int, page: int = 1, page_size: int = 20) -> dict:
    """Helper to create pagination metadata"""
    total_pages = (total + page_size - 1) // page_size
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page * page_size < total,
        "has_prev": page > 1,
    }
