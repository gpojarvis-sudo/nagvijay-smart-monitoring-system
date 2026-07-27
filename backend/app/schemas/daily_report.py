from datetime import date
from typing import Optional
from pydantic import BaseModel

class DailyReportBase(BaseModel):
    office_id: str
    office_name: str
    office_code: Optional[str] = None
    report_date: date
    sb_opened: int = 0
    sb_closed: int = 0
    net_accounts: int = 0
    pli_policies: int = 0
    sum_assured: float = 0.0
    premium: float = 0.0
    speed_post_document: int = 0
    speed_post_parcel: int = 0
    business_post: int = 0
    logistics: int = 0
    international_letter: int = 0
    aadhaar_transactions: int = 0
    aadhaar_amount: float = 0.0

class DailyReportCreate(DailyReportBase):
    pass

class DailyReportResponse(DailyReportBase):
    id: int

    class Config:
        from_attributes = True

class DailyReportSummary(BaseModel):
    total_offices: int
    total_sb_opened: int
    total_sb_closed: int
    total_net_accounts: int
    total_pli_policies: int
    total_sum_assured: float
    total_premium: float
    total_revenue: float  # sum of all revenue fields
    report_date: date
