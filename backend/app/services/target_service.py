"""
Target Service - Core business logic for target engine
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.target import Scheme, Target, TargetAllocation, Achievement
from app.repositories.target_repository import SchemeRepository, TargetRepository, TargetAllocationRepository, AchievementRepository
from app.schemas.target import SchemeCreate, SchemeUpdate, TargetCreate, TargetUpdate, AllocationCreate, AchievementCreate

logger = structlog.get_logger(__name__)


class TargetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scheme_repo = SchemeRepository(db)
        self.target_repo = TargetRepository(db)
        self.allocation_repo = TargetAllocationRepository(db)
        self.achievement_repo = AchievementRepository(db)
    
    # Scheme
    async def create_scheme(self, data: SchemeCreate) -> Scheme:
        existing = await self.scheme_repo.get_by_code(data.scheme_code)
        if existing:
            raise ConflictException(f"Scheme code {data.scheme_code} already exists")
        scheme = await self.scheme_repo.create(data.model_dump())
        logger.info("scheme_created", scheme_id=scheme.id)
        return scheme
    
    async def list_schemes(self, skip: int = 0, limit: int = 50, filters: Optional[Dict] = None):
        return await self.scheme_repo.get_all(skip=skip, limit=limit, filters=filters)
    
    async def get_scheme(self, scheme_id: str) -> Scheme:
        scheme = await self.scheme_repo.get_by_id(scheme_id)
        if not scheme:
            raise NotFoundException(f"Scheme {scheme_id} not found")
        return scheme
    
    async def update_scheme(self, scheme_id: str, data: SchemeUpdate) -> Scheme:
        scheme = await self.get_scheme(scheme_id)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.scheme_repo.update(scheme_id, update_data)
    
    # Target
    async def create_target(self, data: TargetCreate, created_by: Optional[str] = None) -> Target:
        # Validate scheme
        scheme = await self.scheme_repo.get_by_id(data.scheme_id)
        if not scheme:
            raise NotFoundException(f"Scheme {data.scheme_id} not found")
        
        if data.start_date >= data.end_date:
            raise BadRequestException("Start date must be before end date")
        
        target_data = data.model_dump()
        target_data["created_by"] = created_by
        
        target = await self.target_repo.create(target_data)
        logger.info("target_created", target_id=target.id, scheme_id=data.scheme_id)
        return target
    
    async def list_targets(self, skip: int = 0, limit: int = 20, filters: Optional[Dict] = None):
        return await self.target_repo.get_all(skip=skip, limit=limit, filters=filters)
    
    async def get_target(self, target_id: str) -> Target:
        target = await self.target_repo.get_by_id(target_id)
        if not target:
            raise NotFoundException(f"Target {target_id} not found")
        return target
    
    # Allocation
    async def allocate_target(self, data: AllocationCreate, created_by: Optional[str] = None) -> TargetAllocation:
        target = await self.target_repo.get_by_id(data.target_id)
        if not target:
            raise NotFoundException(f"Target {data.target_id} not found")
        
        scheme = await self.scheme_repo.get_by_id(data.scheme_id)
        if not scheme:
            raise NotFoundException(f"Scheme {data.scheme_id} not found")
        
        alloc_data = data.model_dump()
        alloc_data["created_by"] = created_by
        
        allocation = await self.allocation_repo.create(alloc_data)
        logger.info("target_allocated", allocation_id=allocation.id, target_id=data.target_id)
        return allocation
    
    async def bulk_allocate(self, target_id: str, allocations: List[AllocationCreate], financial_year: str, created_by: Optional[str] = None) -> Dict:
        target = await self.get_target(target_id)
        
        created = []
        errors = []
        total_allocated = 0.0
        
        for alloc_data in allocations:
            try:
                # Ensure target_id matches
                alloc_data.target_id = target_id
                allocation = await self.allocate_target(alloc_data, created_by=created_by)
                created.append(allocation)
                total_allocated += allocation.allocated_target
            except Exception as e:
                errors.append({"office_id": alloc_data.office_id, "error": str(e)})
        
        # Update target total if needed - check if allocated exceeds total
        if total_allocated > target.total_target:
            logger.warning("allocation_exceeds_target", target_id=target_id, allocated=total_allocated, total=target.total_target)
        
        return {
            "created_count": len(created),
            "error_count": len(errors),
            "total_allocated": total_allocated,
            "created": created,
            "errors": errors,
        }
    
    async def list_allocations(self, filters: Optional[Dict] = None, skip: int = 0, limit: int = 50):
        return await self.allocation_repo.get_all(skip=skip, limit=limit, filters=filters)
    
    # Achievement
    async def record_achievement(self, data: AchievementCreate, created_by: Optional[str] = None) -> Achievement:
        # Validate allocation
        allocation = await self.allocation_repo.get_by_id(data.allocation_id)
        if not allocation:
            raise NotFoundException(f"Allocation {data.allocation_id} not found")
        
        # Check duplicate source_id for idempotency (Google Forms)
        if data.source_id:
            existing = await self.achievement_repo.get_by_source(data.source_id)
            if existing:
                raise ConflictException(f"Achievement with source_id {data.source_id} already exists")
        
        ach_data = data.model_dump()
        ach_data["created_by"] = created_by
        
        achievement = await self.achievement_repo.create(ach_data)
        
        # Update allocation achieved
        total = await self.achievement_repo.get_total_achieved_for_allocation(data.allocation_id)
        achievement_percentage = (total / allocation.allocated_target * 100) if allocation.allocated_target > 0 else 0
        
        await self.allocation_repo.update(data.allocation_id, {
            "achieved": total,
            "achievement_percentage": min(achievement_percentage, 100.0)
        })
        
        # Update main target
        target = await self.target_repo.get_by_id(data.target_id)
        if target:
            # Sum all allocations achieved for this target
            result = await self.db.execute(
                select(func.coalesce(func.sum(TargetAllocation.achieved), 0)).where(TargetAllocation.target_id == data.target_id)
            )
            total_achieved = float(result.scalar() or 0)
            perc = (total_achieved / target.total_target * 100) if target.total_target > 0 else 0
            await self.target_repo.update(data.target_id, {
                "total_achieved": total_achieved,
                "achievement_percentage": min(perc, 100.0)
            })
        
        logger.info("achievement_recorded", achievement_id=achievement.id, amount=data.amount)
        return achievement
    
    async def list_achievements(self, skip: int = 0, limit: int = 50, filters: Optional[Dict] = None):
        return await self.achievement_repo.get_all(skip=skip, limit=limit, filters=filters, order_by="achievement_date", order_desc=True)
