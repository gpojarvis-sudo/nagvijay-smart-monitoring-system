"""
Office validators
"""
from __future__ import annotations

import re
from typing import Optional

from app.core.exceptions import ValidationException


def validate_pincode(pincode: str) -> str:
    """Validate India pincode - 6 digits, starting with non-zero"""
    if not re.match(r"^[1-9][0-9]{5}$", pincode):
        raise ValidationException(f"Invalid pincode: {pincode}. Must be 6 digits starting 1-9")
    return pincode


def validate_office_code(code: str) -> str:
    """Validate office code format: e.g., NG-123, NAGPUR-HO-001"""
    if not code or len(code) < 2:
        raise ValidationException("Office code must be at least 2 characters")
    if not re.match(r"^[A-Z0-9\-_]+$", code.upper()):
        raise ValidationException("Office code can contain only A-Z, 0-9, -, _")
    return code.upper()


def validate_latitude(lat: Optional[float]) -> Optional[float]:
    if lat is None:
        return None
    if not -90 <= lat <= 90:
        raise ValidationException(f"Invalid latitude {lat}: must be -90 to 90")
    return lat


def validate_longitude(lng: Optional[float]) -> Optional[float]:
    if lng is None:
        return None
    if not -180 <= lng <= 180:
        raise ValidationException(f"Invalid longitude {lng}: must be -180 to 180")
    return lng
