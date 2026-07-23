"""
Office repository
"""
from __future__ import annotations

from typing import Optional, List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.office import Office
from app.repositories.base import BaseRepository
from app.constants.status import OfficeType, OfficeStatus


class OfficeRepository(BaseRepository[Office]):
    def __init__(self, db: AsyncSession):
        super().__init__(Office, db)
    
    async def get_by_code(self, office_code: str) -> Optional[Office]:
        result = await self.db.execute(select(Office).where(Office.office_code == office_code))
        return result.scalars().first()
    
    async def get_by_division(self, division: str) -> List[Office]:
        result = await self.db.execute(select(Office).where(Office.division == division))
        return list(result.scalars().all())
    
    async def get_hierarchy(self, office_id: str) -> Dict:
        """Get office with its children recursively"""
        office = await self.get_by_id(office_id)
        if not office:
            return {}
        
        # Get children
        result = await self.db.execute(select(Office).where(Office.parent_office_id == office_id))
        children = list(result.scalars().all())
        
        return {
            "office": office,
            "children": children,
            "children_count": len(children),
        }
    
    async def get_stats(self) -> Dict:
        """Get office statistics"""
        # Total
        total_result = await self.db.execute(select(func.count()).select_from(Office))
        total = total_result.scalar() or 0
        
        # By type
        by_type_result = await self.db.execute(
            select(Office.office_type, func.count()).group_by(Office.office_type)
        )
        by_type = {str(row[0]): row[1] for row in by_type_result.all()}
        
        # By status
        by_status_result = await self.db.execute(
            select(Office.status, func.count()).group_by(Office.status)
        )
        by_status = {str(row[0]): row[1] for row in by_status_result.all()}
        
        # By division
        by_div_result = await self.db.execute(
            select(Office.division, func.count()).group_by(Office.division)
        )
        by_division = {row[0]: row[1] for row in by_div_result.all()}
        
        return {
            "total_offices": total,
            "by_type": by_type,
            "by_status": by_status,
            "by_division": by_division,
        }
