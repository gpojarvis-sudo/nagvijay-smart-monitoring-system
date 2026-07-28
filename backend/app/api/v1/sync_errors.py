from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.sync_error_service import SyncErrorService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/sync-errors", tags=["Sync Errors"])

class SyncErrorResponse(BaseModel):
    id: int
    error_date: str
    office_name: Optional[str]
    office_code: Optional[str]
    error_type: str
    error_message: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/recent", response_model=list[SyncErrorResponse])
async def get_recent_errors(
    limit: int = Query(default=10, ge=1, le=100),
    error_type: Optional[str] = Query(default=None, description="Filter by error type: SYNC or WEBHOOK"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = SyncErrorService(db)
    errors = await service.get_recent_errors(limit=limit, error_type=error_type)
    return errors
