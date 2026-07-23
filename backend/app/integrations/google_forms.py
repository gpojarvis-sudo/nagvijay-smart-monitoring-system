"""
Google Forms Integration - Webhook receiver and parser
For field data collection from India Post employees
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List

import structlog
from datetime import datetime

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class GoogleFormsIntegration:
    """Handles Google Forms webhook payloads"""
    
    @staticmethod
    def parse_form_response(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Google Forms response payload
        Expected from Apps Script webhook or Google Forms API
        
        Example payload:
        {
          "formId": "...",
          "responseId": "...",
          "timestamp": "...",
          "answers": {
            "office_code": "NG-001",
            "employee_code": "EMP-001",
            "scheme": "PLI",
            "amount": 5,
            ...
          }
        }
        """
        
        try:
            # Support multiple payload formats
            answers = payload.get("answers") or payload.get("responses") or payload
            
            # Normalize fields - India Post specific
            parsed = {
                "form_id": payload.get("formId") or payload.get("form_id"),
                "response_id": payload.get("responseId") or payload.get("response_id") or payload.get("id"),
                "timestamp": payload.get("timestamp") or datetime.utcnow().isoformat(),
                "office_code": answers.get("office_code") or answers.get("Office Code") or answers.get("officeCode"),
                "employee_code": answers.get("employee_code") or answers.get("Employee Code") or answers.get("employeeCode"),
                "scheme_code": answers.get("scheme_code") or answers.get("Scheme") or answers.get("scheme"),
                "achievement_date": answers.get("achievement_date") or answers.get("Date") or answers.get("date"),
                "amount": answers.get("amount") or answers.get("Amount") or answers.get("count") or 1,
                "remarks": answers.get("remarks") or answers.get("Remarks"),
                "raw_payload": payload,
            }
            
            # Clean amount
            try:
                parsed["amount"] = float(parsed["amount"])
            except (ValueError, TypeError):
                parsed["amount"] = 1.0
            
            logger.info("form_response_parsed", response_id=parsed["response_id"], office_code=parsed["office_code"])
            return parsed
        
        except Exception as e:
            logger.error("form_parsing_failed", error=str(e), payload=payload)
            raise ValueError(f"Failed to parse form response: {str(e)}")
    
    @staticmethod
    async def validate_webhook_secret(secret: Optional[str]) -> bool:
        """Validate webhook secret for security"""
        
        if not settings.GOOGLE_FORMS_WEBHOOK_SECRET:
            # If no secret configured, allow all (for MVP)
            logger.warning("forms_webhook_secret_not_configured")
            return True
        
        if not secret:
            return False
        
        return secret == settings.GOOGLE_FORMS_WEBHOOK_SECRET
    
    @staticmethod
    def map_to_achievement(parsed: Dict[str, Any], office_id: str, scheme_id: str, allocation_id: str, target_id: str) -> Dict[str, Any]:
        """Map parsed form data to achievement create schema"""
        
        from datetime import date
        
        achievement_date = parsed.get("achievement_date")
        if isinstance(achievement_date, str):
            try:
                achievement_date = date.fromisoformat(achievement_date.split("T")[0])
            except Exception:
                achievement_date = date.today()
        elif not achievement_date:
            achievement_date = date.today()
        
        return {
            "allocation_id": allocation_id,
            "target_id": target_id,
            "scheme_id": scheme_id,
            "office_id": office_id,
            "achievement_date": achievement_date,
            "amount": parsed["amount"],
            "count": int(parsed["amount"]) if parsed["amount"] >= 1 else 1,
            "source": "GOOGLE_FORM",
            "source_id": parsed["response_id"],
            "remarks": parsed.get("remarks"),
            "additional_data": parsed["raw_payload"],
        }


# Apps Script sample for Google Forms webhook (to be added in Google Forms > Apps Script)
APPS_SCRIPT_WEBHOOK_SAMPLE = """
// Google Apps Script - Paste in Forms > Extensions > Apps Script
// Configure WEBHOOK_URL and WEBHOOK_SECRET

const WEBHOOK_URL = 'https://your-backend.railway.app/api/v1/integrations/forms/webhook';
const WEBHOOK_SECRET = 'your-webhook-secret';

function onFormSubmit(e) {
  const form = FormApp.getActiveForm();
  const response = e.response;
  const itemResponses = response.getItemResponses();
  
  const answers = {};
  for (let i = 0; i < itemResponses.length; i++) {
    const itemResponse = itemResponses[i];
    const title = itemResponse.getItem().getTitle();
    const value = itemResponse.getResponse();
    answers[title] = value;
  }
  
  const payload = {
    formId: form.getId(),
    responseId: response.getId(),
    timestamp: new Date().toISOString(),
    answers: answers
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    headers: {
      'X-Webhook-Secret': WEBHOOK_SECRET
    }
  };
  
  try {
    const res = UrlFetchApp.fetch(WEBHOOK_URL, options);
    Logger.log('Webhook sent: ' + res.getResponseCode());
  } catch (error) {
    Logger.log('Webhook failed: ' + error);
  }
}
"""
