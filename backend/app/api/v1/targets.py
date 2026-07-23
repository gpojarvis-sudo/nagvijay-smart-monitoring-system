"""
Targets API - Schemes, Targets, Allocations, Achievements
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
from app.schemas.target import SchemeCreate, SchemeUpdate, SchemeResponse, TargetCreate, TargetUpdate, TargetResponse, AllocationCreate, AllocationResponse, AchievementCreate, AchievementResponse, BulkAllocationRequest
from app.services.target_service import TargetService

router = APIRouter()


# Schemes
@router.get("/schemes", response_model=dict, summary="List Schemes")
async def list_schemes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    financial_year: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = {}
    if financial_year:
        filters["financial_year"] = financial_year
    if is_active is not None:
        filters["is_active"] = is_active
    
    service = TargetService(db)
    items, total = await service.list_schemes(skip=(page-1)*page_size, limit=page_size, filters=filters)
    
    return {
        "success": True,
        "data": [SchemeResponse.model_validate(s).model_dump() for s in items],
        "pagination": {"total": total, "page": page, "page_size": page_size, "total_pages": (total+page_size-1)//page_size},
    }


@router.post("/schemes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_scheme(
    data: SchemeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TARGET_CREATE)),
):
    service = TargetService(db)
    scheme = await service.create_scheme(data)
    return {"success": True, "data": SchemeResponse.model_validate(scheme).model_dump(), "message": "Scheme created"}


@router.get("/schemes/{scheme_id}", response_model=dict)
async def get_scheme(
    scheme_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TargetService(db)
    scheme = await service.get_scheme(scheme_id)
    return {"success": True, "data": SchemeResponse.model_validate(scheme).model_dump()}


@router.put("/schemes/{scheme_id}", response_model=dict)
async def update_scheme(
    scheme_id: str,
    data: SchemeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TARGET_UPDATE)),
):
    service = TargetService(db)
    scheme = await service.update_scheme(scheme_id, data)
    return {"success": True, "data": SchemeResponse.model_validate(scheme).model_dump()}


# Targets
@router.get("", response_model=dict, summary="List Targets")
async def list_targets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    financial_year: Optional[str] = Query(default=None),
    division: Optional[str] = Query(default=None),
    scheme_id: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = {}
    if financial_year:
        filters["financial_year"] = financial_year
    if division:
        filters["division"] = division
    if scheme_id:
        filters["scheme_id"] = scheme_id
    
    service = TargetService(db)
    items, total = await service.list_targets(skip=(page-1)*page_size, limit=page_size, filters=filters)
    
    return {
        "success": True,
        "data": [TargetResponse.model_validate(t).model_dump() for t in items],
        "pagination": {"total": total, "page": page, "page_size": page_size, "total_pages": (total+page_size-1)//page_size},
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_target(
    data: TargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TARGET_CREATE)),
):
    service = TargetService(db)
    target = await service.create_target(data, created_by=current_user.id)
    return {"success": True, "data": TargetResponse.model_validate(target).model_dump(), "message": "Target created"}


@router.get("/{target_id}", response_model=dict)
async def get_target(
    target_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TargetService(db)
    target = await service.get_target(target_id)
    return {"success": True, "data": TargetResponse.model_validate(target).model_dump()}


# Allocations
@router.get("/{target_id}/allocations", response_model=dict, summary="List Allocations for Target")
async def list_allocations(
    target_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    office_id: Optional[str] = Query(default=None),
    financial_year: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = {"target_id": target_id}
    if office_id:
        filters["office_id"] = office_id
    if financial_year:
        filters["financial_year"] = financial_year
    
    service = TargetService(db)
    items, total = await service.list_allocations(filters=filters, skip=(page-1)*page_size, limit=page_size)
    
    return {
        "success": True,
        "data": [AllocationResponse.model_validate(a).model_dump() for a in items],
        "pagination": {"total": total, "page": page, "page_size": page_size},
    }


@router.post("/allocations", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Allocate Target")
async def allocate_target(
    data: AllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TARGET_ALLOCATE)),
):
    service = TargetService(db)
    alloc = await service.allocate_target(data, created_by=current_user.id)
    return {"success": True, "data": AllocationResponse.model_validate(alloc).model_dump(), "message": "Target allocated"}


@router.post("/{target_id}/allocations/bulk", response_model=dict, summary="Bulk Allocate")
async def bulk_allocate(
    target_id: str,
    data: BulkAllocationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TARGET_ALLOCATE)),
):
    service = TargetService(db)
    result = await service.bulk_allocate(target_id=target_id, allocations=data.allocations, financial_year=data.financial_year, created_by=current_user.id)
    return {
        "success": True,
        "data": {
            "created_count": result["created_count"],
            "error_count": result["error_count"],
            "total_allocated": result["total_allocated"],
            "errors": result["errors"],
        },
        "message": f"Bulk allocated {result['created_count']} entries",
    }


# Achievements
@router.get("/achievements/list", response_model=dict, summary="List Achievements")
async def list_achievements(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    office_id: Optional[str] = Query(default=None),
    scheme_id: Optional[str] = Query(default=None),
    is_verified: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = {}
    if office_id:
        filters["office_id"] = office_id
    if scheme_id:
        filters["scheme_id"] = scheme_id
    if is_verified is not None:
        filters["is_verified"] = is_verified
    
    service = TargetService(db)
    items, total = await service.list_achievements(skip=(page-1)*page_size, limit=page_size, filters=filters)
    
    return {
        "success": True,
        "data": [AchievementResponse.model_validate(a).model_dump() for a in items],
        "pagination": {"total": total, "page": page, "page_size": page_size, "total_pages": (total+page_size-1)//page_size},
    }


@router.post("/achievements", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Record Achievement")
async def record_achievement(
    data: AchievementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TargetService(db)
    ach = await service.record_achievement(data, created_by=current_user.id)
    return {"success": True, "data": AchievementResponse.model_validate(ach).model_dump(), "message": "Achievement recorded"}
