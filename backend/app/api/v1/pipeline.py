from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.end_of_day_pipeline import EndOfDayPipeline

router = APIRouter(tags=["Pipeline"])

@router.post("/eod-run")
async def trigger_eod_pipeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    pipeline = EndOfDayPipeline(db)
    result = await pipeline.run()
    return {"success": True, "data": result}
