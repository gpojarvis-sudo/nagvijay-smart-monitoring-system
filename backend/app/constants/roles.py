"""
User Roles and Permissions - RBAC for India Post hierarchy
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    DIVISION_ADMIN = "DIVISION_ADMIN"
    OFFICE_ADMIN = "OFFICE_ADMIN"
    EMPLOYEE = "EMPLOYEE"
    AUDITOR = "AUDITOR"


ROLE_HIERARCHY: Dict[UserRole, int] = {
    UserRole.SUPER_ADMIN: 100,
    UserRole.DIVISION_ADMIN: 80,
    UserRole.OFFICE_ADMIN: 60,
    UserRole.AUDITOR: 40,
    UserRole.EMPLOYEE: 20,
}

# Permission definitions
class Permission(str, Enum):
    # Office
    OFFICE_CREATE = "office:create"
    OFFICE_READ = "office:read"
    OFFICE_UPDATE = "office:update"
    OFFICE_DELETE = "office:delete"
    OFFICE_BULK_IMPORT = "office:bulk_import"
    
    # Employee
    EMPLOYEE_CREATE = "employee:create"
    EMPLOYEE_READ = "employee:read"
    EMPLOYEE_UPDATE = "employee:update"
    EMPLOYEE_DELETE = "employee:delete"
    
    # Targets
    TARGET_CREATE = "target:create"
    TARGET_READ = "target:read"
    TARGET_UPDATE = "target:update"
    TARGET_DELETE = "target:delete"
    TARGET_ALLOCATE = "target:allocate"
    TARGET_APPROVE = "target:approve"
    
    # Analytics & Reports
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    REPORTS_READ = "reports:read"
    REPORTS_GENERATE = "reports:generate"
    
    # AI
    AI_CHAT = "ai:chat"
    AI_ADMIN = "ai:admin"
    
    # Admin
    USER_MANAGE = "user:manage"
    SETTINGS_MANAGE = "settings:manage"
    AUDIT_READ = "audit:read"
    
    # Integrations
    INTEGRATION_MANAGE = "integration:manage"
    INTEGRATION_READ = "integration:read"


ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.SUPER_ADMIN: list(Permission),  # All permissions
    
    UserRole.DIVISION_ADMIN: [
        Permission.OFFICE_CREATE, Permission.OFFICE_READ, Permission.OFFICE_UPDATE,
        Permission.OFFICE_BULK_IMPORT,
        Permission.EMPLOYEE_CREATE, Permission.EMPLOYEE_READ, Permission.EMPLOYEE_UPDATE, Permission.EMPLOYEE_DELETE,
        Permission.TARGET_CREATE, Permission.TARGET_READ, Permission.TARGET_UPDATE, Permission.TARGET_ALLOCATE, Permission.TARGET_APPROVE,
        Permission.ANALYTICS_READ, Permission.ANALYTICS_EXPORT,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE,
        Permission.AI_CHAT,
        Permission.AUDIT_READ,
        Permission.INTEGRATION_READ, Permission.INTEGRATION_MANAGE,
        Permission.USER_MANAGE,
    ],
    
    UserRole.OFFICE_ADMIN: [
        Permission.OFFICE_READ, Permission.OFFICE_UPDATE,
        Permission.EMPLOYEE_READ, Permission.EMPLOYEE_UPDATE,
        Permission.TARGET_CREATE, Permission.TARGET_READ, Permission.TARGET_UPDATE,
        Permission.ANALYTICS_READ,
        Permission.REPORTS_READ,
        Permission.AI_CHAT,
        Permission.INTEGRATION_READ,
    ],
    
    UserRole.EMPLOYEE: [
        Permission.OFFICE_READ,
        Permission.EMPLOYEE_READ,
        Permission.TARGET_READ, Permission.TARGET_UPDATE,  # Can update own achievements
        Permission.ANALYTICS_READ,
        Permission.REPORTS_READ,
        Permission.AI_CHAT,
    ],
    
    UserRole.AUDITOR: [
        Permission.OFFICE_READ,
        Permission.EMPLOYEE_READ,
        Permission.TARGET_READ,
        Permission.ANALYTICS_READ, Permission.ANALYTICS_EXPORT,
        Permission.REPORTS_READ, Permission.REPORTS_GENERATE,
        Permission.AUDIT_READ,
        Permission.AI_CHAT,
    ],
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])


def can_access_role(requester_role: UserRole, target_role: UserRole) -> bool:
    """Check if requester can manage target role (hierarchy)"""
    return ROLE_HIERARCHY.get(requester_role, 0) >= ROLE_HIERARCHY.get(target_role, 0)
