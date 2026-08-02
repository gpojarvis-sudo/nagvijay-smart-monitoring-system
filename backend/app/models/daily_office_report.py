from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class DailyOfficeReport(Base):
    __tablename__ = "daily_office_reports"

    __table_args__ = (
        UniqueConstraint(
            "office_id",
            "report_date",
            name="uq_daily_office_report_office_date",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    office_id = Column(String(36), ForeignKey("offices.id"), nullable=False, index=True)

    office_name = Column(String(255), nullable=False)
    office_code = Column(String(100), nullable=True)

    report_date = Column(Date, nullable=False, index=True)

    # Savings
    sb_opened = Column(Integer, default=0, nullable=False)
    sb_closed = Column(Integer, default=0, nullable=False)
    net_accounts = Column(Integer, default=0, nullable=False)

    # PLI
    pli_policies = Column(Integer, default=0, nullable=False)
    sum_assured = Column(Numeric(18, 2), default=0, nullable=False)
    premium = Column(Numeric(18, 2), default=0, nullable=False)

    # Revenue
    speed_post_document = Column(Integer, default=0, nullable=False)
    speed_post_parcel = Column(Integer, default=0, nullable=False)
    business_post = Column(Integer, default=0, nullable=False)
    logistics = Column(Integer, default=0, nullable=False)
    international_letter = Column(Integer, default=0, nullable=False)

    # Aadhaar
    aadhaar_transactions = Column(Integer, default=0, nullable=False)
    aadhaar_amount = Column(Numeric(18, 2), default=0, nullable=False)


    # Background Sync
    sync_status = Column(String(20), default="PENDING", nullable=False, index=True)
    retry_count = Column(Integer, default=0, nullable=False)
    synced_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_error = Column(String(1000), nullable=True)
    sheet_row_number = Column(Integer, nullable=True)

    office = relationship("Office", backref="daily_reports")