from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_office_report import DailyOfficeReport
from app.repositories.base import BaseRepository


class DailyOfficeReportRepository(BaseRepository[DailyOfficeReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyOfficeReport, db)

    async def get_by_office_and_date(
        self,
        office_id: str,
        report_date: date,
    ) -> Optional[DailyOfficeReport]:
        result = await self.db.execute(
            select(DailyOfficeReport).where(
                DailyOfficeReport.office_id == office_id,
                DailyOfficeReport.report_date == report_date,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_reports(self):
        result = await self.db.execute(
            select(DailyOfficeReport)
        )
        return result.scalars().all()

    async def get_reports(self, stmt):
        result = await self.db.execute(stmt)
        return result.scalars().all()

