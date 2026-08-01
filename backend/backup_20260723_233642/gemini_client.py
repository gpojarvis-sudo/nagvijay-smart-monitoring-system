"""
Gemini AI Client - Google Generative AI
"""
from __future__ import annotations

from typing import Optional, Dict, Any, List
import asyncio

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class GeminiClient:
    """Gemini client wrapper"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        
        self.model = None
        self._initialized = False
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self._initialized = True
                logger.info("gemini_client_initialized", model=self.model_name)
            except Exception as e:
                logger.error("gemini_init_failed", error=str(e))
        else:
            logger.warning("gemini_api_key_missing")
    
    def is_configured(self) -> bool:
        return self._initialized and self.model is not None
    
    async def generate_response(
        self,
        message: str,
        context: Optional[str] = None,
        conversation_id: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate response from Gemini"""
        
        if not self.is_configured():
            raise ValueError("Gemini client not configured - set GEMINI_API_KEY")
        
        # Build prompt with context
        full_prompt = ""
        if context:
            full_prompt += f"{context}\n\n"
        if history:
            for turn in history[-5:]:  # Last 5 turns
                role = turn.get("role", "user")
                content = turn.get("content", "")
                full_prompt += f"{role}: {content}\n"
        
        full_prompt += f"User Query: {message}\n\nAssistant Response (be concise, professional, India Post context):"
        
        try:
            # Run in thread pool since google-generativeai is sync
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    }
                )
            )
            
            text = response.text if hasattr(response, 'text') else str(response)
            logger.info("gemini_response_generated", conversation_id=conversation_id, prompt_length=len(full_prompt))
            return text
        
        except Exception as e:
            logger.error("gemini_generation_failed", error=str(e))
            # Fallback response
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> str:
        """Fallback when Gemini fails"""
        msg_lower = message.lower()
        
        if "top performer" in msg_lower:
            return "Top performers are offices with highest achievement percentage. Check Dashboard > Top Performers section for current rankings. You can filter by scheme, division, and financial year."
        elif "low performer" in msg_lower or "needs attention" in msg_lower:
            return "Low performing offices require immediate intervention. Review their target allocation vs capacity, provide training support, and consider reallocation. Check Analytics for details."
        elif "report" in msg_lower:
            return "You can generate reports from Reports section: Daily DPR, Monthly Consolidated, Office-wise, Scheme-wise. Export as PDF/Excel. Scheduled reports can be configured via Settings."
        elif "target" in msg_lower:
            return "Targets are allocated at Division level and distributed to offices/employees. Use Target Engine to allocate, track achievements via manual entry, Google Forms, or Sheets sync."
        else:
            return f"I understand you're asking about '{message}'. In NagVijay system, you can view this data in Dashboard, Analytics, and Reports sections. For specific insights, please check the relevant module or generate a report. Overall system is tracking {settings.APP_NAME} for Nagpur City Division."
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Gemini health"""
        if not self.is_configured():
            return {"status": "not_configured", "message": "GEMINI_API_KEY missing"}
        
        try:
            response = await self.generate_response("Hello - health check", context="Respond with 'OK' if you can see this.")
            return {"status": "healthy", "model": self.model_name, "response_sample": response[:100]}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Global client
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
