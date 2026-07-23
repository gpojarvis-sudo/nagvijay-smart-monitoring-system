"""
Employee repository
"""
from __future__ import annotations

from typing import List, Dict, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: AsyncSession):
        super().__init__(Employee, db)
    
    async def get_by_code(self, employee_code: str) -> Optional[Employee]:
        result = await self.db.execute(select(Employee).where(Employee.employee_code == employee_code))
        return result.scalars().first()
    
    async def get_by_office(self, office_id: str) -> List[Employee]:
        result = await self.db.execute(select(Employee).where(Employee.office_id == office_id))
        return list(result.scalars().all())
    
    async def get_by_designation(self, designation: str) -> List[Employee]:
        result = await self.db.execute(select(Employee).where(Employee.designation == designation))
        return list(result.scalars().all())
    
    async def get_stats(self) -> Dict:
        total_result = await self.db.execute(select(func.count()).select_from(Employee))
        total = total_result.scalar() or 0
        
        by_designation = await self.db.execute(
            select(Employee.designation, func.count()).group_by(Employee.designation)
        )
        by_desig = {str(row[0]): row[1] for row in by_designation.all()}
        
        by_status = await self.db.execute(
            select(Employee.status, func.count()).group_by(Employee.status)
        )
        by_stat = {str(row[0]): row[1] for row in by_status.all()}
        
        by_office = await self.db.execute(
            select(Employee.office_id, func.count()).group_by(Employee.office_id)
        )
        by_off = {row[0]: row[1] for row in by_office.all()}
        
        return {
            "total": total,
            "by_designation": by_desig,
            "by_status": by_stat,
            "by_office": by_off,
        }
