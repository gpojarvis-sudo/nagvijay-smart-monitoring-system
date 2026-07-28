"""
AI Insights Service – Generates daily insights using Gemini
"""
from datetime import date
from typing import Dict, Any, Optional
import structlog
from app.integrations.gemini_client import get_gemini_client
from app.services.daily_office_report_service import DailyOfficeReportService
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class AIInsightsService:
    def __init__(self, db):
        self.db = db
        self.daily_service = DailyOfficeReportService(db)
        self.gemini = get_gemini_client()

    async def generate_insights(self, report_date: date, division: str = "Nagpur City") -> Dict[str, Any]:
        """Generate AI insights for a given date"""
        
        # Check if Gemini is configured
        if not self.gemini.is_configured():
            return {
                "status": "not_configured",
                "message": "GEMINI_API_KEY is not set. Please configure it in environment variables.",
                "insights": None
            }

        # Fetch daily summary and office-wise data
        summary = await self.daily_service.get_summary(report_date=report_date, division=division)
        reports = await self.daily_service.get_reports(report_date=report_date, division=division)

        # Prepare data for prompt
        office_list = []
        for r in reports[:20]:  # Limit to 20 offices for prompt size
            office_list.append(
                f"Office: {r.office_name} | SB Opened: {r.sb_opened} | SB Closed: {r.sb_closed} | "
                f"Net Accounts: {r.net_accounts} | PLI Policies: {r.pli_policies} | "
                f"Revenue: {r.speed_post_document + r.speed_post_parcel + r.business_post + r.logistics + r.international_letter}"
            )

        prompt = f"""
You are an AI assistant for India Post, Nagpur City Division.
Analyze the following daily office report data for {report_date.isoformat()} and provide concise insights.

**Summary:**
- Total Offices Reporting: {summary['total_offices']}
- Total SB Opened: {summary['total_sb_opened']}
- Total SB Closed: {summary['total_sb_closed']}
- Net Accounts Added: {summary['total_net_accounts']}
- Total PLI Policies: {summary['total_pli_policies']}
- Total Premium (₹): {summary['total_premium']}
- Total Sum Assured (₹): {summary['total_sum_assured']}
- Total Aadhaar Transactions: {summary.get('aadhaar_transactions', 0)}
- Total Revenue (₹): {summary['total_revenue']}

**Top 20 Offices (by revenue/performance):**
{chr(10).join(office_list)}

Based on this data, please provide:
1. Key performance highlights (top 3 achievements).
2. Areas needing attention (offices with low activity, if any).
3. Anomalies or unusual patterns (if any).
4. A brief overall summary.

Keep your response concise, professional, and actionable. Use bullet points where appropriate.
"""

        # Call Gemini
        try:
            response = await self.gemini.generate_text(prompt)
            return {
                "status": "success",
                "report_date": report_date.isoformat(),
                "division": division,
                "insights": response,
                "summary": summary,
                "office_count": len(reports)
            }
        except Exception as e:
            logger.error("ai_insights_failed", error=str(e))
            return {
                "status": "error",
                "report_date": report_date.isoformat(),
                "division": division,
                "error": str(e),
                "insights": None
            }
