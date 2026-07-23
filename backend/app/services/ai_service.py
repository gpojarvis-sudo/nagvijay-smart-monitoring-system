"""
AI Service - Gemini integration for chatbot and insights
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.integrations.gemini_client import GeminiClient
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsFilter

logger = structlog.get_logger(__name__)
settings = get_settings()


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = AnalyticsService(db)
        self.gemini_client = GeminiClient() if settings.GEMINI_API_KEY else None
    
    async def chat(self, message: str, conversation_id: Optional[str] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """AI Chatbot - context-aware with analytics"""
        
        if not self.gemini_client:
            return {
                "response": "AI assistant is not configured. Please set GEMINI_API_KEY in environment.",
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "sources": [],
                "suggestions": ["Configure Gemini API key", "Check AI settings"],
            }
        
        try:
            # Get current stats for context
            filters = AnalyticsFilter()
            if user_context and "division" in user_context:
                filters.division = user_context["division"]
            
            stats = await self.analytics_service.get_dashboard_stats(filters)
            
            # Build context for Gemini
            context_prompt = self._build_context_prompt(stats, user_context)
            
            # Call Gemini
            response_text = await self.gemini_client.generate_response(
                message=message,
                context=context_prompt,
                conversation_id=conversation_id,
            )
            
            # Generate suggestions based on query
            suggestions = await self._generate_suggestions(message, stats)
            
            return {
                "response": response_text,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "sources": [
                    {"type": "analytics", "data": stats.kpis.model_dump()},
                ],
                "suggestions": suggestions,
            }
        
        except Exception as e:
            logger.error("ai_chat_failed", error=str(e))
            return {
                "response": f"I encountered an error while processing your request. Error: {str(e)}. Please try again or contact support.",
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "sources": [],
                "suggestions": ["Try rephrasing your question", "Check recent reports", "View dashboard"],
            }
    
    def _build_context_prompt(self, stats: Any, user_context: Optional[Dict] = None) -> str:
        """Build context for Gemini"""
        
        kpis = stats.kpis
        
        context = f"""
You are NagVijay AI Assistant, an expert analytics assistant for India Post's NagVijay Smart Monitoring System.

Current System Status (Nagpur City Division - MVP):

KPIs:
- Total Offices: {kpis.total_offices}
- Total Employees: {kpis.total_employees}
- Total Targets: {kpis.total_targets}
- Total Achieved: {kpis.total_achieved}
- Overall Achievement: {kpis.overall_achievement_percentage}%
- Active Schemes: {kpis.active_schemes}
- Pending Verifications: {kpis.pending_verifications}

Top Performers: {stats.top_performers[:3]}
Low Performers: {stats.low_performers[:3]}

Schemes: PLI, RPLI, SSA, TD, RD, Business Parcel, Speed Post, IPPB

Your role:
- Answer queries about performance, targets, offices, employees
- Provide insights, identify anomalies, suggest actions
- Be concise, professional, helpful for India Post officers
- Use data from context when relevant
- Suggest actionable next steps

User Context: {user_context or 'General user'}

Important: Never hallucinate data not in context. If unsure, say you need more specific data.

Current Date: {datetime.utcnow().isoformat()}
Division: Nagpur City (Scalable to Region, Circle, National)
"""
        return context
    
    async def _generate_suggestions(self, message: str, stats: Any) -> List[str]:
        """Generate follow-up suggestions"""
        
        suggestions = []
        msg_lower = message.lower()
        
        if "performance" in msg_lower or "achievement" in msg_lower:
            suggestions = [
                "Show top performing offices",
                "What are low performing schemes?",
                "Generate monthly report",
            ]
        elif "office" in msg_lower:
            suggestions = [
                "Show office hierarchy",
                "Employee count by office",
                "Office-wise target allocation",
            ]
        elif "target" in msg_lower:
            suggestions = [
                "Scheme-wise achievement",
                "Pending verifications",
                "Daily performance report",
            ]
        else:
            suggestions = [
                "Show overall dashboard stats",
                "Which offices need attention?",
                "Generate today's DPR",
                "Compare with last month",
            ]
        
        return suggestions[:3]
    
    async def analyze_anomalies(self) -> Dict[str, Any]:
        """Anomaly detection"""
        
        filters = AnalyticsFilter()
        stats = await self.analytics_service.get_dashboard_stats(filters)
        
        anomalies = []
        
        # Low performers with high targets
        for performer in stats.low_performers:
            if performer.get("percentage", 0) < 30 and performer.get("target", 0) > 50:
                anomalies.append({
                    "type": "LOW_PERFORMANCE_HIGH_TARGET",
                    "office": performer.get("office_name"),
                    "percentage": performer.get("percentage"),
                    "target": performer.get("target"),
                    "severity": "HIGH",
                    "suggestion": f"Office {performer.get('office_name')} has only {performer.get('percentage')}% achievement against high target. Needs immediate attention.",
                })
        
        # Check pending verifications
        if stats.kpis.pending_verifications > 20:
            anomalies.append({
                "type": "PENDING_VERIFICATIONS",
                "count": stats.kpis.pending_verifications,
                "severity": "MEDIUM",
                "suggestion": f"{stats.kpis.pending_verifications} achievements pending verification. Please verify to update accurate stats.",
            })
        
        # Overall low achievement
        if stats.kpis.overall_achievement_percentage < 50:
            anomalies.append({
                "type": "LOW_OVERALL_ACHIEVEMENT",
                "percentage": stats.kpis.overall_achievement_percentage,
                "severity": "HIGH",
                "suggestion": f"Overall achievement is {stats.kpis.overall_achievement_percentage}%. Needs intervention across division.",
            })
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    async def summarize_report(self, report_data: Dict[str, Any]) -> str:
        """Summarize report using Gemini"""
        
        if not self.gemini_client:
            return "AI summarization not available - Gemini API key not configured."
        
        try:
            prompt = f"Summarize this India Post performance report in 3-4 bullet points for a Division Head. Be concise, professional, highlight key numbers:\n\n{report_data}"
            response = await self.gemini_client.generate_response(message=prompt)
            return response
        except Exception as e:
            logger.error("report_summarization_failed", error=str(e))
            return f"Report generated with {report_data.get('kpis', {}).get('total_offices', 0)} offices and {report_data.get('kpis', {}).get('overall_achievement_percentage', 0)}% achievement."
