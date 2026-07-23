"""Schemas package"""
from .common import PaginatedResponse, SuccessResponse, ErrorResponse, PaginationParams
from .auth import TokenResponse, GoogleAuthRequest, RefreshTokenRequest, UserInfo
from .user import UserCreate, UserUpdate, UserResponse
from .office import OfficeCreate, OfficeUpdate, OfficeResponse, OfficeBulkImport
from .employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from .target import SchemeCreate, SchemeResponse, TargetCreate, TargetResponse, AchievementCreate
from .analytics import DashboardStats, AnalyticsFilter

__all__ = [
    "PaginatedResponse", "SuccessResponse", "ErrorResponse", "PaginationParams",
    "TokenResponse", "GoogleAuthRequest", "RefreshTokenRequest", "UserInfo",
    "UserCreate", "UserUpdate", "UserResponse",
    "OfficeCreate", "OfficeUpdate", "OfficeResponse", "OfficeBulkImport",
    "EmployeeCreate", "EmployeeUpdate", "EmployeeResponse",
    "SchemeCreate", "SchemeResponse", "TargetCreate", "TargetResponse", "AchievementCreate",
    "DashboardStats", "AnalyticsFilter"
]
