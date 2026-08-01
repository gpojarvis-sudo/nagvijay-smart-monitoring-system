from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_office_report import DailyOfficeReport
from app.repositories.base import BaseRepository


class DailyOfficeReportRepository(BaseRepository[DailyOfficeReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(DailyOfficeReport, db)
