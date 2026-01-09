"""
Data models for RBAC
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model"""
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True


@dataclass
class RoleAssignment:
    """Role assignment model"""
    user_id: str
    role_id: str
    assigned_at: Optional[datetime] = None
