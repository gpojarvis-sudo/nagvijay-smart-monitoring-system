from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.ai_insights_service import AIInsightsService

router = APIRouter(prefix="/ai-insights", tags=["AI Insights"])

@router.get("/daily")
async def get_daily_insights(
    report_date: date = Query(..., description="Date in YYYY-MM-DD"),
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = AIInsightsService(db)
    result = await service.generate_insights(report_date=report_date, division=division)
    return result
