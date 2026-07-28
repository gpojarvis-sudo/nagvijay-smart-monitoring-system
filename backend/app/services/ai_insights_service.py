"""
AI Insights Service – Generates daily insights using configured AI provider (Cloudflare/Gemini)
"""
from datetime import date
from typing import Dict, Any
import structlog
from app.core.config import get_settings
from app.services.daily_office_report_service import DailyOfficeReportService

logger = structlog.get_logger(__name__)
settings = get_settings()


class AIInsightsService:
    def __init__(self, db):
        self.db = db
        self.daily_service = DailyOfficeReportService(db)
        self.ai_client = self._get_ai_client()

    def _get_ai_client(self):
        """Return the appropriate AI client based on settings.AI_PROVIDER"""
        if settings.AI_PROVIDER == "cloudflare":
            from app.integrations.cloudflare_client import CloudflareClient
            return CloudflareClient()
        else:
            from app.integrations.gemini_client import get_gemini_client
            return get_gemini_client()

    async def generate_insights(self, report_date: date, division: str = "Nagpur City") -> Dict[str, Any]:
        if not self.ai_client.is_configured():
            return {
                "status": "not_configured",
                "message": f"{settings.AI_PROVIDER.upper()} is not configured. Please set required environment variables.",
                "insights": None
            }

        summary = await self.daily_service.get_summary(report_date=report_date, division=division)
        reports = await self.daily_service.get_reports(report_date=report_date, division=division)

        office_list = []
        for r in reports[:20]:
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

        try:
            response = await self.ai_client.generate_text(prompt)
            return {
                "status": "success",
                "report_date": report_date.isoformat(),
                "division": division,
                "provider": settings.AI_PROVIDER,
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
                "provider": settings.AI_PROVIDER,
                "error": str(e),
                "insights": None
            }
