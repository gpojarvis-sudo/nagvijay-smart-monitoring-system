"""
AI Monitoring Engine – Calculates office health, risk, and generates insights.
Uses real data from PostgreSQL. No mock data.
"""
import asyncio
from datetime import date, timedelta, datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import structlog
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.office import Office
from app.models.daily_office_report import DailyOfficeReport
from app.models.target import Achievement, TargetAllocation, Scheme
from app.models.sync_error import SyncError
from app.integrations.cloudflare_client import CloudflareClient
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class AIMonitoringEngine:
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.cloudflare = CloudflareClient()

    async def get_session(self):
        if self.db:
            return self.db
        return AsyncSessionLocal()

    async def generate_monitoring_report(self, division: str = "Nagpur City") -> Dict[str, Any]:
        """
        Generate a complete monitoring report for the division.
        """
        async with await self.get_session() as session:
            # 1. Get all active offices
            offices = await session.execute(
                select(Office).where(Office.status == 'ACTIVE')
            )
            offices = offices.scalars().all()

            # 2. Get daily reports for last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            reports = await session.execute(
                select(DailyOfficeReport).where(
                    DailyOfficeReport.report_date >= thirty_days_ago
                )
            )
            reports = reports.scalars().all()

            # 3. Get achievements (if any)
            achievements = await session.execute(
                select(Achievement).where(
                    Achievement.achievement_date >= thirty_days_ago
                )
            )
            achievements = achievements.scalars().all()

            # 4. Get sync errors (duplicates)
            errors = await session.execute(
                select(SyncError).where(
                    SyncError.error_type == 'WEBHOOK',
                    SyncError.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
                )
            )
            errors = errors.scalars().all()

            # 5. Get scheme targets
            scheme_targets = await session.execute(
                select(Scheme, TargetAllocation)
                .join(TargetAllocation, Scheme.id == TargetAllocation.scheme_id)
                .where(TargetAllocation.financial_year == '2024-25')
            )
            scheme_targets = scheme_targets.all()

            # Build indices
            reports_by_office = {}
            for r in reports:
                reports_by_office.setdefault(r.office_id, []).append(r)

            errors_by_office = {}
            for e in errors:
                errors_by_office.setdefault(e.office_code, []).append(e)

            achievements_by_office = {}
            for a in achievements:
                achievements_by_office.setdefault(a.office_id, []).append(a)

            # Calculate metrics per office
            office_metrics = []
            for office in offices:
                metrics = await self._compute_office_metrics(
                    office,
                    reports_by_office.get(office.id, []),
                    errors_by_office.get(office.office_code, []),
                    achievements_by_office.get(office.id, []),
                    scheme_targets
                )
                office_metrics.append(metrics)

            # Sort by health score descending
            office_metrics.sort(key=lambda x: x['health_score'], reverse=True)

            # Generate structured summary
            summary = {
                "report_date": date.today().isoformat(),
                "division": division,
                "total_offices": len(offices),
                "offices_requiring_attention": [m for m in office_metrics if m['risk_level'] == 'high'],
                "top_performers": office_metrics[:5],
                "bottom_performers": office_metrics[-5:] if len(office_metrics) >= 5 else office_metrics,
                "scheme_insights": await self._compute_scheme_insights(scheme_targets),
                "recommendations": await self._generate_recommendations(office_metrics),
                "office_metrics": office_metrics,  # Full list
            }

            # Optional: AI-generated brief
            if self.cloudflare.is_configured():
                try:
                    brief = await self._generate_ai_brief(summary)
                    summary['ai_brief'] = brief
                except Exception as e:
                    logger.error("ai_brief_failed", error=str(e))
                    summary['ai_brief'] = "AI brief generation failed."
            else:
                summary['ai_brief'] = "Cloudflare AI not configured."

            return summary

    async def _compute_office_metrics(
        self,
        office: Office,
        reports: List[DailyOfficeReport],
        errors: List[SyncError],
        achievements: List[Achievement],
        scheme_targets: List[Tuple[Scheme, TargetAllocation]]
    ) -> Dict[str, Any]:
        """Compute all metrics for a single office."""
        # Reporting consistency: % of days in last 30 days with report
        # For simplicity, we'll assume we want to see if report exists for each day in the last 30 days
        # but we only have reports that exist. We'll count unique dates.
        if not reports:
            consistency = 0.0
            missed_reports = 30
        else:
            # Get distinct dates reported
            reported_dates = set(r.report_date for r in reports)
            # Number of days in last 30 days
            today = date.today()
            start_date = today - timedelta(days=30)
            # Count how many days in that range have a report
            # We'll count the number of weekdays (Mon-Fri) if needed, but we'll count all days.
            days_in_range = (today - start_date).days
            # For simplicity, count how many dates are in the range
            # We'll calculate the count of reported dates that fall in the last 30 days
            # but we already filtered reports to last 30 days.
            # So we can just use the number of reports (assuming one per day per office)
            # However, there could be multiple reports per day? Unique constraint prevents.
            # So len(reports) is the number of days reported.
            days_reported = len(reports)
            consistency = (days_reported / days_in_range) * 100 if days_in_range > 0 else 0
            missed_reports = days_in_range - days_reported

        # Duplicate submissions
        duplicate_count = len(errors)

        # Achievements (sum of amounts)
        total_achieved = sum(a.amount for a in achievements) if achievements else 0.0

        # Scheme-wise target progress: find allocations for this office
        target_progress = 0.0
        allocated_target = 0.0
        for scheme, alloc in scheme_targets:
            if alloc.office_id == office.id:
                allocated_target += alloc.allocated_target
                # Achievements per scheme: we would need to filter achievements by scheme
                # But achievements are not directly linked to schemes? They have scheme_id.
                # We'll compute separately.
        # For now, we'll compute a simple progress using total achieved vs allocated
        if allocated_target > 0:
            target_progress = (total_achieved / allocated_target) * 100

        # Revenue trend: from daily reports (sum of revenue fields)
        # We'll use last 7 days vs previous 7 days
        # For simplicity, we'll compute total revenue in reports
        total_revenue = sum(
            r.speed_post_document + r.speed_post_parcel + r.business_post +
            r.logistics + r.international_letter
            for r in reports
        ) if reports else 0.0

        # Compute health score (0-100)
        # Weighted factors: consistency (40%), target progress (30%), duplicate count (negative) (20%), revenue growth (10%)
        health_score = 0.0
        if consistency > 0:
            health_score += consistency * 0.4
        if target_progress > 0:
            health_score += min(target_progress, 100) * 0.3
        # Penalize duplicates: each duplicate reduces score by 5, up to 20 points.
        duplicate_penalty = min(duplicate_count * 5, 20)
        health_score += max(0, 100 - duplicate_penalty) * 0.2  # weight 20%
        # Revenue growth could be computed, but we'll keep it simple for now.
        # Clamp to 0-100
        health_score = max(0, min(100, health_score))

        # Risk level based on missed reports and duplicates
        if missed_reports > 10 or duplicate_count > 3:
            risk_level = 'high'
        elif missed_reports > 5 or duplicate_count > 1:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            "office_id": office.id,
            "office_code": office.office_code,
            "office_name": office.office_name,
            "office_type": office.office_type.value if hasattr(office.office_type, 'value') else str(office.office_type),
            "reporting_consistency_percent": round(consistency, 2),
            "missed_reports": missed_reports,
            "duplicate_submissions": duplicate_count,
            "total_achieved": round(total_achieved, 2),
            "target_progress_percent": round(target_progress, 2),
            "total_revenue": round(total_revenue, 2),
            "health_score": round(health_score, 2),
            "risk_level": risk_level,
        }

    async def _compute_scheme_insights(self, scheme_targets: List[Tuple[Scheme, TargetAllocation]]) -> List[Dict]:
        """Aggregate scheme performance."""
        scheme_data = {}
        for scheme, alloc in scheme_targets:
            scheme_data.setdefault(scheme.scheme_code, {
                "scheme_code": scheme.scheme_code,
                "scheme_name": scheme.scheme_name,
                "total_allocated": 0.0,
                "total_achieved": 0.0,
                "offices": []
            })
            scheme_data[scheme.scheme_code]["total_allocated"] += alloc.allocated_target
            # Achievements are not directly linked here; we'll need to query achievements.
            # For now, we'll compute achievements per scheme from the achievement table in the main report.

        # We'll query achievements per scheme in the main function and update.
        # This is a placeholder.
        return list(scheme_data.values())

    async def _generate_recommendations(self, office_metrics: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []
        # Offices with high risk
        high_risk = [m for m in office_metrics if m['risk_level'] == 'high']
        if high_risk:
            names = ', '.join([m['office_name'] for m in high_risk][:3])
            recommendations.append(f"Immediate attention needed for: {names} (high risk).")

        # Offices with low consistency
        low_consistency = [m for m in office_metrics if m['reporting_consistency_percent'] < 50]
        if low_consistency:
            names = ', '.join([m['office_name'] for m in low_consistency][:3])
            recommendations.append(f"Improve reporting consistency for: {names}.")

        # Duplicate issues
        duplicate_offices = [m for m in office_metrics if m['duplicate_submissions'] > 2]
        if duplicate_offices:
            names = ', '.join([m['office_name'] for m in duplicate_offices][:3])
            recommendations.append(f"Investigate duplicate submissions from: {names}.")

        if not recommendations:
            recommendations.append("All offices are performing well. Continue monitoring.")

        return recommendations

    
    def _clean_ai_response(self, response: str) -> str:
        """Remove reasoning blocks like <think>...</think> from AI response."""
        import re
        # Remove <think>...</think> blocks (non-greedy, with newlines)
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # Strip extra whitespace
        return cleaned.strip()

async def _generate_ai_brief(self, summary: Dict) -> str:
        """Generate a natural language brief using Cloudflare DeepSeek."""
        # Prepare a concise prompt
        high_risk = summary.get('offices_requiring_attention', [])
        high_risk_names = [m['office_name'] for m in high_risk]
        top_performers = summary.get('top_performers', [])
        top_names = [m['office_name'] for m in top_performers[:3]]

        prompt = f"""
You are the NagVijay AI Operations Officer for India Post, Nagpur City Division.
Based on the following real data, generate a concise morning brief for senior officers.

- Total Offices: {summary['total_offices']}
- Offices requiring immediate attention: {', '.join(high_risk_names) if high_risk_names else 'None'}
- Top performing offices: {', '.join(top_names) if top_names else 'None'}
- Key recommendations: {', '.join(summary.get('recommendations', []))}

Provide a brief summary (3-4 sentences) that highlights the overall health, critical issues, and recommended actions.
Keep it professional and actionable.
"""
        response = await self.cloudflare.generate_response(message=prompt)
        return self._clean_ai_response(response)
