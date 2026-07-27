"""
Sync Error Model - Logs errors from webhook and sync processes
"""
from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SAEnum, Text
from app.core.database import Base
from app.constants.status import SyncErrorType


class SyncError(Base):
    __tablename__ = "sync_errors"

    id = Column(Integer, primary_key=True, index=True)
    error_date = Column(Date, nullable=False, index=True)  # the date of the report being processed
    office_name = Column(String(255), nullable=True)       # office name from the submission
    office_code = Column(String(100), nullable=True)       # office code if available
    error_type = Column(SAEnum(SyncErrorType), nullable=False)
    error_message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
