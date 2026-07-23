"""
Target repositories - Schemes, Targets, Allocations, Achievements
"""
from __future__ import annotations

from typing import List, Optional, Dict
from datetime import date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.target import Scheme, Target, TargetAllocation, Achievement
from app.repositories.base import BaseRepository


class SchemeRepository(BaseRepository[Scheme]):
    def __init__(self, db: AsyncSession):
        super().__init__(Scheme, db)
    
    async def get_by_code(self, scheme_code: str) -> Optional[Scheme]:
        result = await self.db.execute(select(Scheme).where(Scheme.scheme_code == scheme_code))
        return result.scalars().first()
    
    async def get_active(self) -> List[Scheme]:
        result = await self.db.execute(select(Scheme).where(Scheme.is_active == True))
        return list(result.scalars().all())
    
    async def get_by_financial_year(self, fy: str) -> List[Scheme]:
        result = await self.db.execute(select(Scheme).where(Scheme.financial_year == fy))
        return list(result.scalars().all())


class TargetRepository(BaseRepository[Target]):
    def __init__(self, db: AsyncSession):
        super().__init__(Target, db)
    
    async def get_by_scheme_and_fy(self, scheme_id: str, fy: str, division: Optional[str] = None) -> List[Target]:
        query = select(Target).where(and_(Target.scheme_id == scheme_id, Target.financial_year == fy))
        if division:
            query = query.where(Target.division == division)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class TargetAllocationRepository(BaseRepository[TargetAllocation]):
    def __init__(self, db: AsyncSession):
        super().__init__(TargetAllocation, db)
    
    async def get_by_target(self, target_id: str) -> List[TargetAllocation]:
        result = await self.db.execute(select(TargetAllocation).where(TargetAllocation.target_id == target_id))
        return list(result.scalars().all())
    
    async def get_by_office(self, office_id: str, fy: Optional[str] = None) -> List[TargetAllocation]:
        query = select(TargetAllocation).where(TargetAllocation.office_id == office_id)
        if fy:
            query = query.where(TargetAllocation.financial_year == fy)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_employee(self, employee_id: str) -> List[TargetAllocation]:
        result = await self.db.execute(select(TargetAllocation).where(TargetAllocation.employee_id == employee_id))
        return list(result.scalars().all())


class AchievementRepository(BaseRepository[Achievement]):
    def __init__(self, db: AsyncSession):
        super().__init__(Achievement, db)
    
    async def get_by_date_range(self, start: date, end: date, office_id: Optional[str] = None) -> List[Achievement]:
        query = select(Achievement).where(and_(Achievement.achievement_date >= start, Achievement.achievement_date <= end))
        if office_id:
            query = query.where(Achievement.office_id == office_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_source(self, source_id: str) -> Optional[Achievement]:
        result = await self.db.execute(select(Achievement).where(Achievement.source_id == source_id))
        return result.scalars().first()
    
    async def get_pending_verification(self) -> List[Achievement]:
        result = await self.db.execute(select(Achievement).where(Achievement.is_verified == False))
        return list(result.scalars().all())
    
    async def get_total_achieved_for_allocation(self, allocation_id: str) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Achievement.amount), 0)).where(Achievement.allocation_id == allocation_id)
        )
        return float(result.scalar() or 0)


# Aliases for backward compatibility
TargetRepo = TargetRepository
SchemeRepositoryAlias = SchemeRepository
AchievementRepositoryAlias = AchievementRepository
