"""
Notification Service
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notification import Notification
from app.constants.status import NotificationType
from app.repositories.base import BaseRepository

logger = structlog.get_logger(__name__)


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        office_id: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        notif_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "office_id": office_id,
            "title": title,
            "message": message,
            "type": type,
            "action_url": action_url,
            "metadata_json": metadata,
        }
        notification = await self.repo.create(notif_data)
        logger.info("notification_created", notification_id=notification.id, user_id=user_id, type=type)
        
        # Trigger n8n webhook if enabled
        await self._trigger_n8n_webhook(notification)
        
        return notification
    
    async def create_bulk(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        **kwargs
    ) -> List[Notification]:
        notifications = []
        for user_id in user_ids:
            notif = await self.create_notification(user_id=user_id, title=title, message=message, type=type, **kwargs)
            notifications.append(notif)
        return notifications
    
    async def get_user_notifications(self, user_id: str, skip: int = 0, limit: int = 20, unread_only: bool = False):
        filters = {"user_id": user_id}
        if unread_only:
            filters["is_read"] = False
        return await self.repo.get_all(skip=skip, limit=limit, filters=filters, order_by="created_at", order_desc=True)
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        notif = result.scalars().first()
        if not notif:
            return False
        
        await self.repo.update(notification_id, {"is_read": True, "read_at": datetime.now(timezone.utc)})
        return True
    
    async def mark_all_as_read(self, user_id: str) -> int:
        from sqlalchemy import update
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        return result.rowcount
    
    async def _trigger_n8n_webhook(self, notification: Notification):
        """Trigger n8n workflow for external notifications (email, etc)"""
        from app.core.config import get_settings
        from app.integrations.n8n_client import trigger_n8n_workflow
        
        settings = get_settings()
        if not settings.N8N_ENABLED or not settings.N8N_WEBHOOK_URL:
            return
        
        try:
            await trigger_n8n_workflow(
                event="notification_created",
                payload={
                    "notification_id": notification.id,
                    "user_id": notification.user_id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type.value if hasattr(notification.type, 'value') else str(notification.type),
                }
            )
        except Exception as e:
            logger.warning("n8n_webhook_failed", error=str(e))
