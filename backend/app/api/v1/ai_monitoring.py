from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.ai_monitoring_service import AIMonitoringEngine
import traceback

router = APIRouter(prefix="/ai-monitoring", tags=["AI Monitoring"])

@router.get("/summary")
async def get_monitoring_summary(
    division: str = Query(default="Nagpur City"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        engine = AIMonitoringEngine(db)
        report = await engine.generate_monitoring_report(division=division)
        return report
    except Exception as e:
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print("=" * 80)
        print("AI MONITORING ERROR:")
        print(error_detail)
        print("=" * 80)
        raise HTTPException(status_code=500, detail=error_detail)
