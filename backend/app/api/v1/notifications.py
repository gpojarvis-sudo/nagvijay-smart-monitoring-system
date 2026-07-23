"""
Notifications API
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=dict, summary="List Notifications")
async def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NotificationService(db)
    skip = (page - 1) * page_size
    items, total = await service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        unread_only=unread_only,
    )
    
    # Convert to dict
    data = []
    for n in items:
        data.append({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type.value if hasattr(n.type, 'value') else str(n.type),
            "is_read": n.is_read,
            "action_url": n.action_url,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        })
    
    return {
        "success": True,
        "data": data,
        "pagination": {"total": total, "page": page, "page_size": page_size, "total_pages": (total+page_size-1)//page_size},
    }


@router.put("/{notification_id}/read", response_model=dict, summary="Mark as Read")
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NotificationService(db)
    success = await service.mark_as_read(notification_id, current_user.id)
    if not success:
        return {"success": False, "message": "Notification not found"}
    return {"success": True, "message": "Marked as read"}


@router.put("/read-all", response_model=dict, summary="Mark All as Read")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return {"success": True, "data": {"marked_count": count}, "message": f"Marked {count} notifications as read"}
