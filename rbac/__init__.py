"""
RBAC Framework for Semantic Data Chatbot
Provides role-based access control for agent operations
"""

from .framework import RBACFramework, Role, Permission
from .decorators import require_permission, require_role
from .models import User, RoleAssignment

__all__ = [
    'RBACFramework',
    'Role',
    'Permission',
    'require_permission',
    'require_role',
    'User',
    'RoleAssignment',
]
