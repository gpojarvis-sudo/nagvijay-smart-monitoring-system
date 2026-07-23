"""
Audit Log - Immutable audit trail
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SAEnum, func, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.constants.status import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Actor
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Action
    action: Mapped[AuditAction] = mapped_column(SAEnum(AuditAction), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "office", "employee", "target"
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<Audit {self.action} {self.resource_type}:{self.resource_id} by {self.user_email}>"
