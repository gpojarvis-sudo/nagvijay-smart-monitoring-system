"""
Status enums for domain entities
"""
from __future__ import annotations

from enum import Enum


class OfficeType(str, Enum):
    HEAD_OFFICE = "HEAD_OFFICE"  # HO
    SUB_OFFICE = "SUB_OFFICE"  # SO
    BRANCH_OFFICE = "BRANCH_OFFICE"  # BO
    ADMIN_OFFICE = "ADMIN_OFFICE"  # Divisional Office, Circle Office
    OTHER = "OTHER"


class OfficeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TEMP_CLOSED = "TEMP_CLOSED"
    PERM_CLOSED = "PERM_CLOSED"


class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TRANSFERRED = "TRANSFERRED"
    RETIRED = "RETIRED"
    SUSPENDED = "SUSPENDED"
    DEPUTATION = "DEPUTATION"


class EmployeeCategory(str, Enum):
    GENERAL = "GENERAL"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"


class Designation(str, Enum):
    # Gazetted
    SSP = "SSP"  # Senior Superintendent
    SP = "SP"
    ASP = "ASP"
    IP = "IP"  # Inspector Posts
    ASP_IP = "ASP_IP"
    
    # Non-Gazetted
    SPM = "SPM"  # Sub Postmaster
    BPM = "BPM"  # Branch Postmaster
    ABPM = "ABPM"
    PA = "PA"  # Postal Assistant
    SA = "SA"  # Sorting Assistant
    MTS = "MTS"
    GDS = "GDS"
    POSTMAN = "POSTMAN"
    OTHER = "OTHER"


class TargetStatus(str, Enum):
    DRAFT = "DRAFT"
    ALLOCATED = "ALLOCATED"
    IN_PROGRESS = "IN_PROGRESS"
    ACHIEVED = "ACHIEVED"
    PARTIALLY_ACHIEVED = "PARTIALLY_ACHIEVED"
    NOT_ACHIEVED = "NOT_ACHIEVED"
    CARRIED_FORWARD = "CARRIED_FORWARD"


class SchemeType(str, Enum):
    PLI = "PLI"  # Postal Life Insurance
    RPLI = "RPLI"  # Rural PLI
    SSA = "SSA"  # Sukanya Samriddhi
    TD = "TD"  # Time Deposit
    RD = "RD"  # Recurring Deposit
    PPF = "PPF"
    NSC = "NSC"
    KVP = "KVP"
    BUSINESS_PARCEL = "BUSINESS_PARCEL"
    SPEED_POST = "SPEED_POST"
    ECOMMERCE = "ECOMMERCE"
    AADHAAR = "AADHAAR"
    IPPB = "IPPB"  # India Post Payments Bank
    OTHER = "OTHER"


class AchievementSource(str, Enum):
    MANUAL = "MANUAL"
    GOOGLE_FORM = "GOOGLE_FORM"
    GOOGLE_SHEET = "GOOGLE_SHEET"
    API = "API"
    BULK_IMPORT = "BULK_IMPORT"
    N8N = "N8N"


class NotificationType(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TARGET_ALERT = "TARGET_ALERT"
    ACHIEVEMENT_MILESTONE = "ACHIEVEMENT_MILESTONE"
    SYSTEM = "SYSTEM"


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    ALLOCATE = "ALLOCATE"
