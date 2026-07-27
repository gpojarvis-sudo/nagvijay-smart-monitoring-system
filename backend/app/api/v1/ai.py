"""
AI API - Gemini Chatbot and insights
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.analytics import AIChatRequest
from app.services.ai_service import AIService

router = APIRouter()
settings = get_settings()


@router.post("/chat", response_model=dict, summary="AI Chatbot")
async def ai_chat(
    request: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    
):
    """
    Chat with NagVijay AI Assistant powered by Gemini.
    Context-aware with dashboard analytics.
    """
    
    if not settings.ENABLE_AI_CHATBOT:
        return {
            "success": False,
            "message": "AI chatbot is disabled",
            "data": {
                "response": "AI assistant is currently disabled. Please enable ENABLE_AI_CHATBOT in settings.",
                "conversation_id": request.conversation_id or "disabled",
            }
        }
    
    service = AIService(db)
    
    user_context = {
        "user_id": "dev-user",
        "email": "dev@localhost",
        "role": "admin",
        "office_id": None,
        "division": "Nagpur City",
        "filters": request.context or {},
    }
    
    result = await service.chat(
        message=request.message,
        conversation_id=request.conversation_id,
        user_context=user_context,
    )
    
    return {"success": True, "data": result}


@router.get("/anomalies", response_model=dict, summary="AI Anomaly Detection")
async def detect_anomalies(
    db: AsyncSession = Depends(get_db),
    
):
    """Detect anomalies using AI analysis"""
    service = AIService(db)
    anomalies = await service.analyze_anomalies()
    return {"success": True, "data": anomalies}


@router.get("/health", response_model=dict, summary="AI Service Health")
async def ai_health(
    
):
    from app.integrations.gemini_client import get_gemini_client
    
    client = get_gemini_client()
    health = await client.health_check()
    
    return {
        "success": True,
        "data": {
            "enabled": settings.ENABLE_AI_CHATBOT,
            "configured": client.is_configured(),
            "model": settings.GEMINI_MODEL,
            "health": health,
        }
    }
