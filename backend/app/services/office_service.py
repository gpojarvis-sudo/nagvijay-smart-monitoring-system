"""
Office Service - Business logic for office management
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.office import Office
from app.repositories.office_repository import OfficeRepository
from app.schemas.office import OfficeCreate, OfficeUpdate

logger = structlog.get_logger(__name__)


class OfficeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OfficeRepository(db)
    
    async def create_office(self, data: OfficeCreate, created_by: Optional[str] = None) -> Office:
        # Check duplicate code
        existing = await self.repo.get_by_code(data.office_code)
        if existing:
            raise ConflictException(f"Office code {data.office_code} already exists")
        
        # Validate parent
        if data.parent_office_id:
            parent = await self.repo.get_by_id(data.parent_office_id)
            if not parent:
                raise NotFoundException(f"Parent office {data.parent_office_id} not found")
        
        office_data = data.model_dump()
        office_data["created_by"] = created_by
        
        office = await self.repo.create(office_data)
        logger.info("office_created", office_id=office.id, code=office.office_code)
        return office
    
    async def get_office(self, office_id: str) -> Office:
        office = await self.repo.get_by_id(office_id)
        if not office:
            raise NotFoundException(f"Office {office_id} not found")
        return office
    
    async def list_offices(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> tuple[List[Office], int]:
        return await self.repo.get_all(skip=skip, limit=limit, filters=filters, order_by=sort_by, order_desc=sort_desc)
    
    async def update_office(self, office_id: str, data: OfficeUpdate) -> Office:
        office = await self.get_office(office_id)
        
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        
        # If code change attempted? Not allowed via update - office_code is immutable, but we didn't include in update schema
        updated = await self.repo.update(office_id, update_data)
        logger.info("office_updated", office_id=office_id)
        return updated
    
    async def delete_office(self, office_id: str) -> bool:
        office = await self.get_office(office_id)
        
        # Check if has children
        from sqlalchemy import select
        from app.models.office import Office as OfficeModel
        result = await self.db.execute(select(OfficeModel).where(OfficeModel.parent_office_id == office_id))
        children = result.scalars().all()
        if children:
            raise BadRequestException(f"Cannot delete office with {len(children)} child offices. Reassign or delete children first.")
        
        # Check employees
        from app.models.employee import Employee
        emp_result = await self.db.execute(select(Employee).where(Employee.office_id == office_id))
        employees = emp_result.scalars().all()
        if employees:
            raise BadRequestException(f"Cannot delete office with {len(employees)} employees. Transfer employees first.")
        
        return await self.repo.delete(office_id)
    
    async def get_stats(self) -> Dict:
        return await self.repo.get_stats()
    
    async def bulk_import(self, offices: List[OfficeCreate], created_by: Optional[str] = None) -> Dict:
        created = []
        errors = []
        
        for office_data in offices:
            try:
                office = await self.create_office(office_data, created_by=created_by)
                created.append(office)
            except Exception as e:
                errors.append({"office_code": office_data.office_code, "error": str(e)})
        
        return {
            "created_count": len(created),
            "error_count": len(errors),
            "created": created,
            "errors": errors,
        }
