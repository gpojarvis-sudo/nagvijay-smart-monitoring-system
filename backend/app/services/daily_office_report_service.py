from typing import Optional, List
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_office_report import DailyOfficeReport
from app.models.office import Office


class DailyOfficeReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, data: dict) -> DailyOfficeReport:
        office_code = data.get("office_code")
        office_name = data.get("office_name") or data.get("office_name_original")
        office = None

        if office_code:
            stmt = select(Office).where(Office.office_code == office_code)
            result = await self.db.execute(stmt)
            office = result.scalar_one_or_none()

        if office is None and office_name:
            stmt = select(Office).where(Office.office_name == office_name)
            result = await self.db.execute(stmt)
            office = result.scalar_one_or_none()

        if office is None:
            raise ValueError(f"Office not found: code={office_code}, name={office_name}")

        report_date_str = data.get("report_date")
        if not report_date_str:
            raise ValueError("report_date is required")
        if isinstance(report_date_str, str):
            for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    report_date = date.fromisoformat(report_date_str)  # try ISO first
                    break
                except ValueError:
                    try:
                        from datetime import datetime
                        report_date = datetime.strptime(report_date_str, fmt).date()
                        break
                    except ValueError:
                        continue
            else:
                raise ValueError(f"Invalid date format: {report_date_str}")
        else:
            report_date = report_date_str

        stmt = select(DailyOfficeReport).where(
            DailyOfficeReport.office_id == office.id,
            DailyOfficeReport.report_date == report_date
        )
        result = await self.db.execute(stmt)
        report = result.scalar_one_or_none()

        if report is None:
            report = DailyOfficeReport(
                office_id=office.id,
                office_code=office.office_code,
                office_name=office.office_name,
                report_date=report_date,
            )
            self.db.add(report)

        for key, value in data.items():
            if hasattr(report, key) and key not in ('office_code', 'office_name', 'office_name_original', '_row_number', 'report_date'):
                setattr(report, key, value)

        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_reports(self, report_date: Optional[date] = None, office_id: Optional[str] = None, division: Optional[str] = None) -> List[DailyOfficeReport]:
        from sqlalchemy import and_
        stmt = select(DailyOfficeReport)
        conditions = []
        if report_date:
            conditions.append(DailyOfficeReport.report_date == report_date)
        if office_id:
            conditions.append(DailyOfficeReport.office_id == office_id)
        if division:
            stmt = stmt.join(Office, DailyOfficeReport.office_id == Office.id)
            conditions.append(Office.division == division)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, report_id: int) -> DailyOfficeReport:
        stmt = select(DailyOfficeReport).where(DailyOfficeReport.id == report_id)
        result = await self.db.execute(stmt)
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError(f"Report with id {report_id} not found")
        return report

    async def get_summary(self, report_date: date, division: str = "Nagpur City") -> dict:
        from sqlalchemy import func, and_
        from app.models.office import Office
        stmt = (
            select(
                func.count(DailyOfficeReport.id).label("total_offices"),
                func.sum(DailyOfficeReport.sb_opened).label("total_sb_opened"),
                func.sum(DailyOfficeReport.sb_closed).label("total_sb_closed"),
                func.sum(DailyOfficeReport.net_accounts).label("total_net_accounts"),
                func.sum(DailyOfficeReport.pli_policies).label("total_pli_policies"),
                func.sum(DailyOfficeReport.sum_assured).label("total_sum_assured"),
                func.sum(DailyOfficeReport.premium).label("total_premium"),
                func.sum(
                    DailyOfficeReport.speed_post_document + 
                    DailyOfficeReport.speed_post_parcel + 
                    DailyOfficeReport.business_post + 
                    DailyOfficeReport.logistics + 
                    DailyOfficeReport.international_letter
                ).label("total_revenue"),
            )
            .join(Office, DailyOfficeReport.office_id == Office.id)
            .where(
                and_(
                    DailyOfficeReport.report_date == report_date,
                    Office.division == division
                )
            )
        )
        result = await self.db.execute(stmt)
        row = result.first()
        return {
            "total_offices": row[0] or 0,
            "total_sb_opened": row[1] or 0,
            "total_sb_closed": row[2] or 0,
            "total_net_accounts": row[3] or 0,
            "total_pli_policies": row[4] or 0,
            "total_sum_assured": float(row[5] or 0.0),
            "total_premium": float(row[6] or 0.0),
            "total_revenue": float(row[7] or 0.0),
            "report_date": report_date,
        }
