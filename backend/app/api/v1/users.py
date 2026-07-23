"""
Users API - User management (Admin only)
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.roles import require_permission, require_division_admin
from app.constants.roles import Permission, UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.repositories.user_repository import UserRepository
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter()


@router.get("", response_model=dict, summary="List Users")
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_MANAGE)),
):
    repo = UserRepository(db)
    filters = {}
    if role:
        filters["role"] = role
    if search:
        filters["email"] = search
    if is_active is not None:
        filters["is_active"] = is_active
    
    items, total = await repo.get_all(skip=(page-1)*page_size, limit=page_size, filters=filters)
    
    return {
        "success": True,
        "data": [UserResponse.model_validate(u).model_dump() for u in items],
        "pagination": {"total": total, "page": page, "page_size": page_size, "total_pages": (total+page_size-1)//page_size},
    }


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_MANAGE)),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    return {"success": True, "data": UserResponse.model_validate(user).model_dump()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_MANAGE)),
):
    repo = UserRepository(db)
    existing = await repo.get_by_email(str(data.email))
    if existing:
        raise ConflictException(f"User with email {data.email} already exists")
    
    import uuid
    user_data = data.model_dump()
    user_data["id"] = str(uuid.uuid4())
    user = await repo.create(user_data)
    return {"success": True, "data": UserResponse.model_validate(user).model_dump(), "message": "User created"}


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_MANAGE)),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    
    # Prevent demoting super admin by non-super admin
    if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise ConflictException("Only SUPER_ADMIN can modify another SUPER_ADMIN")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await repo.update(user_id, update_data)
    return {"success": True, "data": UserResponse.model_validate(updated).model_dump(), "message": "User updated"}
