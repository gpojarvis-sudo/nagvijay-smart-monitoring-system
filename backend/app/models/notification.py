"""
Notification model - In-app notifications
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SAEnum, func, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.constants.status import NotificationType


class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Recipient
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    office_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), default=NotificationType.INFO, nullable=False)
    
    # State
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Notification {self.type} to {self.user_id}: {self.title}>"
