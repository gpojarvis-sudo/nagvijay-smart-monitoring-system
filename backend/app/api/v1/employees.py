"""
Employees API
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.roles import require_permission
from app.constants.roles import Permission
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import EmployeeService

router = APIRouter()


@router.get("", response_model=dict, summary="List Employees")
async def list_employees(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    office_id: Optional[str] = Query(default=None),
    designation: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = {}
    if search:
        filters["full_name"] = search
    if office_id:
        filters["office_id"] = office_id
    if designation:
        filters["designation"] = designation
    if status:
        filters["status"] = status
    
    service = EmployeeService(db)
    skip = (page - 1) * page_size
    items, total = await service.list_employees(skip=skip, limit=page_size, filters=filters, sort_by=sort_by, sort_desc=(sort_order == "desc"))
    
    return {
        "success": True,
        "data": [EmployeeResponse.model_validate(e).model_dump() for e in items],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "has_next": page * page_size < total,
            "has_prev": page > 1,
        },
    }


@router.get("/stats", response_model=dict)
async def get_employee_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EmployeeService(db)
    stats = await service.get_stats()
    return {"success": True, "data": stats}


@router.get("/{employee_id}", response_model=dict)
async def get_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = EmployeeService(db)
    emp = await service.get_employee(employee_id)
    return {"success": True, "data": EmployeeResponse.model_validate(emp).model_dump()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EMPLOYEE_CREATE)),
):
    service = EmployeeService(db)
    emp = await service.create_employee(data, created_by=current_user.id)
    return {"success": True, "data": EmployeeResponse.model_validate(emp).model_dump(), "message": "Employee created"}


@router.put("/{employee_id}", response_model=dict)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EMPLOYEE_UPDATE)),
):
    service = EmployeeService(db)
    emp = await service.update_employee(employee_id, data)
    return {"success": True, "data": EmployeeResponse.model_validate(emp).model_dump(), "message": "Employee updated"}


@router.delete("/{employee_id}", response_model=dict)
async def delete_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EMPLOYEE_DELETE)),
):
    service = EmployeeService(db)
    await service.delete_employee(employee_id)
    return {"success": True, "message": "Employee deleted"}
