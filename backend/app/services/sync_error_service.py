from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sync_error import SyncError


class SyncErrorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recent_errors(self, limit: int = 10, error_type: str = None):
        stmt = select(SyncError).order_by(desc(SyncError.id))
        if error_type:
            stmt = stmt.where(SyncError.error_type == error_type)
        stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
