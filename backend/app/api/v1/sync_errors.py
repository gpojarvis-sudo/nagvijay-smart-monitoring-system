from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.sync_error_service import SyncErrorService

router = APIRouter()

@router.get("/recent")
async def get_recent_errors(
    limit: int = Query(default=10, ge=1, le=100),
    error_type: Optional[str] = Query(default=None, description="Filter by error type: SYNC or WEBHOOK"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = SyncErrorService(db)
    errors = await service.get_recent_errors(limit=limit, error_type=error_type)
    return [
        {
            "id": e.id,
            "error_date": str(e.error_date),
            "office_name": e.office_name,
            "office_code": e.office_code,
            "error_type": e.error_type.value if hasattr(e.error_type, 'value') else str(e.error_type),
            "error_message": e.error_message,
            "created_at": e.created_at.isoformat(),
        }
        for e in errors
    ]
