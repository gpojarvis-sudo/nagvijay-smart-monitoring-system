"""
Helper utilities
"""
from __future__ import annotations

import re
import random
import string
from datetime import date, datetime


def generate_code(prefix: str = "", length: int = 6) -> str:
    """Generate random code with prefix, e.g., OFFICE-AB12CD"""
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(random.choice(chars) for _ in range(length))
    if prefix:
        return f"{prefix}-{random_part}"
    return random_part


def get_financial_year(d: date | datetime | None = None) -> str:
    """Get Indian financial year from date - FY starts April 1"""
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    
    # FY: April to March
    if d.month >= 4:
        return f"{d.year}-{str(d.year + 1)[-2:]}"
    else:
        return f"{d.year - 1}-{str(d.year)[-2:]}"


def slugify(text: str) -> str:
    """Convert text to slug"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text


def format_indian_currency(amount: float) -> str:
    """Format amount in Indian currency style"""
    # Simple formatting - can be enhanced with locale
    return f"₹{amount:,.2f}"


def calculate_percentage(achieved: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return round((achieved / target) * 100, 2)


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
