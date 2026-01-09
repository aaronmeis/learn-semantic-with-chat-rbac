"""
RBAC Decorators for permission checking
"""

from functools import wraps
from typing import Callable
from .framework import Permission, RBACFramework


# Global RBAC instance (should be initialized by application)
_rbac_instance: RBACFramework = None


def set_rbac_instance(rbac: RBACFramework):
    """Set the global RBAC instance"""
    global _rbac_instance
    _rbac_instance = rbac


def require_permission(permission: Permission):
    """Decorator to require a specific permission"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _rbac_instance is None:
                raise RuntimeError("RBAC instance not initialized")
            
            # Extract user_id from kwargs or first argument
            user_id = kwargs.get('user_id') or (args[0].user_id if args and hasattr(args[0], 'user_id') else None)
            
            if user_id is None:
                raise ValueError("user_id must be provided")
            
            if not _rbac_instance.check_permission(user_id, permission):
                raise PermissionError(f"User {user_id} does not have permission {permission.value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str):
    """Decorator to require a specific role"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _rbac_instance is None:
                raise RuntimeError("RBAC instance not initialized")
            
            user_id = kwargs.get('user_id') or (args[0].user_id if args and hasattr(args[0], 'user_id') else None)
            
            if user_id is None:
                raise ValueError("user_id must be provided")
            
            user_roles = _rbac_instance.get_user_roles(user_id)
            if role_name not in user_roles:
                raise PermissionError(f"User {user_id} does not have role {role_name}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
