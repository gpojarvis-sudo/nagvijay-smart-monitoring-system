"""
Pipeline State – Tracks last processed row from Response 1 sheet
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base


class PipelineState(Base):
    __tablename__ = "pipeline_state"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
