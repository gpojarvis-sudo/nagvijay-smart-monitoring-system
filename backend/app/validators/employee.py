"""
Employee validators
"""
from __future__ import annotations

import re
from datetime import date

from app.core.exceptions import ValidationException


def validate_employee_code(code: str) -> str:
    if not code or len(code) < 2:
        raise ValidationException("Employee code must be at least 2 characters")
    if not re.match(r"^[A-Z0-9\-_]+$", code.upper()):
        raise ValidationException("Employee code can contain only A-Z, 0-9, -, _")
    return code.upper()


def validate_phone(phone: str) -> str:
    # Indian phone: 10 digits, optionally +91
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if re.match(r"^(\+91|91)?[6-9][0-9]{9}$", cleaned):
        return cleaned[-10:]  # Return last 10 digits
    raise ValidationException(f"Invalid Indian phone number: {phone}")


def validate_doj_dob(dob: date, doj: date):
    if dob and doj and doj <= dob:
        raise ValidationException("Date of joining must be after date of birth")
    if dob and dob > date.today():
        raise ValidationException("Date of birth cannot be in future")
    if doj and doj > date.today():
        raise ValidationException("Date of joining cannot be in future")
