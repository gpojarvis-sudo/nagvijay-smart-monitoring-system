"""
Employee Service
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.employee import Employee
from app.models.office import Office
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

logger = structlog.get_logger(__name__)


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EmployeeRepository(db)
    
    async def create_employee(self, data: EmployeeCreate, created_by: Optional[str] = None) -> Employee:
        existing = await self.repo.get_by_code(data.employee_code)
        if existing:
            raise ConflictException(f"Employee code {data.employee_code} already exists")
        
        # Validate office
        office_result = await self.db.execute(select(Office).where(Office.id == data.office_id))
        office = office_result.scalars().first()
        if not office:
            raise NotFoundException(f"Office {data.office_id} not found")
        
        # Validate reporting manager if provided
        if data.reporting_manager_id:
            manager = await self.repo.get_by_id(data.reporting_manager_id)
            if not manager:
                raise NotFoundException(f"Reporting manager {data.reporting_manager_id} not found")
        
        emp_data = data.model_dump()
        emp_data["created_by"] = created_by
        
        employee = await self.repo.create(emp_data)
        logger.info("employee_created", employee_id=employee.id, code=employee.employee_code)
        return employee
    
    async def get_employee(self, employee_id: str) -> Employee:
        emp = await self.repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee {employee_id} not found")
        return emp
    
    async def list_employees(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> tuple[List[Employee], int]:
        return await self.repo.get_all(skip=skip, limit=limit, filters=filters, order_by=sort_by, order_desc=sort_desc)
    
    async def update_employee(self, employee_id: str, data: EmployeeUpdate) -> Employee:
        emp = await self.get_employee(employee_id)
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        updated = await self.repo.update(employee_id, update_data)
        logger.info("employee_updated", employee_id=employee_id)
        return updated
    
    async def delete_employee(self, employee_id: str) -> bool:
        emp = await self.get_employee(employee_id)
        return await self.repo.delete(employee_id)
    
    async def get_stats(self) -> Dict:
        return await self.repo.get_stats()
