"""
Role and Permission dependencies
"""
from __future__ import annotations

from typing import List, Callable

from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.dependencies.auth import get_current_active_user
from app.constants.roles import UserRole, Permission, has_permission


class RoleChecker:
    """Dependency for role-based access"""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} not authorized. Required: {[r.value for r in self.allowed_roles]}",
            )
        return user


class PermissionChecker:
    """Dependency for permission-based access"""
    
    def __init__(self, required_permissions: List[Permission]):
        self.required_permissions = required_permissions
    
    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        # Super admin bypass
        if user.role == UserRole.SUPER_ADMIN:
            return user
        
        for perm in self.required_permissions:
            if not has_permission(user.role, perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permission: {perm.value}",
                )
        return user


def require_role(*roles: UserRole) -> Callable:
    """Factory for role requirement"""
    return RoleChecker(list(roles))


def require_permission(*permissions: Permission) -> Callable:
    """Factory for permission requirement"""
    return PermissionChecker(list(permissions))


# Common role requirements
require_super_admin = RoleChecker([UserRole.SUPER_ADMIN])
require_division_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.DIVISION_ADMIN])
require_office_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.DIVISION_ADMIN, UserRole.OFFICE_ADMIN])
require_auditor = RoleChecker([UserRole.SUPER_ADMIN, UserRole.AUDITOR, UserRole.DIVISION_ADMIN])
require_any_authenticated = RoleChecker([UserRole.SUPER_ADMIN, UserRole.DIVISION_ADMIN, UserRole.OFFICE_ADMIN, UserRole.EMPLOYEE, UserRole.AUDITOR])
