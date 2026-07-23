"""
Audit log repository
"""
from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)
    
    async def get_by_user(self, user_id: str, limit: int = 50) -> List[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_resource(self, resource_type: str, resource_id: str) -> List[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).where(and_(AuditLog.resource_type == resource_type, AuditLog.resource_id == resource_id)).order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_date_range(self, start: datetime, end: datetime) -> List[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).where(and_(AuditLog.created_at >= start, AuditLog.created_at <= end)).order_by(AuditLog.created_at.desc())
        )
        return list(result.scalars().all())
