"""
Offices API - CRUD for post offices
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.roles import require_permission, require_office_admin, require_division_admin
from app.constants.roles import Permission
from app.models.user import User
from app.schemas.office import OfficeCreate, OfficeUpdate, OfficeResponse, OfficeBulkImport
from app.services.office_service import OfficeService

router = APIRouter()


@router.get("", response_model=dict, summary="List Offices")
async def list_offices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    office_type: Optional[str] = Query(default=None),
    division: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List offices with pagination, search, and filters"""
    
    filters = {}
    if search:
        filters["office_name"] = search  # Repo does ilike for office_name
    if office_type:
        filters["office_type"] = office_type
    if division:
        filters["division"] = division
    if status:
        filters["status"] = status
    
    service = OfficeService(db)
    skip = (page - 1) * page_size
    items, total = await service.list_offices(
        skip=skip,
        limit=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_desc=(sort_order == "desc"),
    )
    
    return {
        "success": True,
        "data": [OfficeResponse.model_validate(o).model_dump() for o in items],
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "has_next": page * page_size < total,
            "has_prev": page > 1,
        },
    }


@router.get("/stats", response_model=dict, summary="Office Stats")
async def get_office_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = OfficeService(db)
    stats = await service.get_stats()
    return {"success": True, "data": stats}


@router.get("/{office_id}", response_model=dict, summary="Get Office by ID")
async def get_office(
    office_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = OfficeService(db)
    office = await service.get_office(office_id)
    return {"success": True, "data": OfficeResponse.model_validate(office).model_dump()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Create Office")
async def create_office(
    data: OfficeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OFFICE_CREATE)),
):
    service = OfficeService(db)
    office = await service.create_office(data, created_by=current_user.id)
    
    # Audit log
    from app.models.audit import AuditLog
    from app.constants.status import AuditAction
    from app.repositories.audit_repository import AuditRepository
    audit_repo = AuditRepository(db)
    await audit_repo.create({
        "id": __import__("uuid").uuid4().__str__(),
        "user_id": current_user.id,
        "user_email": current_user.email,
        "user_role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "action": AuditAction.CREATE,
        "resource_type": "office",
        "resource_id": office.id,
        "description": f"Created office {office.office_code}: {office.office_name}",
        "new_values": data.model_dump(mode='json'),
    })
    
    return {"success": True, "data": OfficeResponse.model_validate(office).model_dump(), "message": "Office created"}


@router.put("/{office_id}", response_model=dict, summary="Update Office")
async def update_office(
    office_id: str,
    data: OfficeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OFFICE_UPDATE)),
):
    service = OfficeService(db)
    office = await service.update_office(office_id, data)
    return {"success": True, "data": OfficeResponse.model_validate(office).model_dump(), "message": "Office updated"}


@router.delete("/{office_id}", response_model=dict, summary="Delete Office")
async def delete_office(
    office_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OFFICE_DELETE)),
):
    service = OfficeService(db)
    await service.delete_office(office_id)
    return {"success": True, "message": "Office deleted"}


@router.post("/bulk-import", response_model=dict, summary="Bulk Import Offices")
async def bulk_import_offices(
    data: OfficeBulkImport,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OFFICE_BULK_IMPORT)),
):
    service = OfficeService(db)
    result = await service.bulk_import(data.offices, created_by=current_user.id)
    
    return {
        "success": True,
        "data": {
            "created_count": result["created_count"],
            "error_count": result["error_count"],
            "errors": result["errors"],
        },
        "message": f"Imported {result['created_count']} offices, {result['error_count']} errors",
    }

@router.get("/stats", summary="Office Statistics by Type")
async def get_office_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from sqlalchemy import func, select
    from app.models.office import Office
    stmt = select(Office.office_type, func.count(Office.id)).group_by(Office.office_type)
    result = await db.execute(stmt)
    counts = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in result}
    total = sum(counts.values())
    return {
        "head_office": counts.get("HEAD_OFFICE", 0),
        "sub_office": counts.get("SUB_OFFICE", 0),
        "branch_office": counts.get("BRANCH_OFFICE", 0),
        "admin_office": counts.get("ADMIN_OFFICE", 0),
        "other": counts.get("OTHER", 0),
        "total": total,
    }
