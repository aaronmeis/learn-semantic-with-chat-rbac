"""
Core RBAC Framework Implementation
"""

from enum import Enum
from typing import Set, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3
import json
import hashlib
from pathlib import Path


class Permission(Enum):
    """System permissions"""
    CHATBOT_EXECUTE = "chatbot:execute"
    VALIDATION_EXECUTE = "validation:execute"
    QUALITY_MONITOR = "quality:monitor"
    QUALITY_ANALYZE = "quality:analyze"
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    POLICY_READ = "policy:read"
    POLICY_WRITE = "policy:write"
    ADMIN_ALL = "admin:all"


@dataclass
class Role:
    """Role definition"""
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""


class RBACFramework:
    """Role-Based Access Control Framework"""
    
    # Predefined roles
    ROLES = {
        "admin": Role(
            name="admin",
            permissions={Permission.ADMIN_ALL},
            description="Full system access"
        ),
        "operator": Role(
            name="operator",
            permissions={
                Permission.CHATBOT_EXECUTE,
                Permission.VALIDATION_EXECUTE,
                Permission.DATA_READ
            },
            description="Can execute and validate chatbot operations"
        ),
        "analyst": Role(
            name="analyst",
            permissions={
                Permission.QUALITY_MONITOR,
                Permission.QUALITY_ANALYZE,
                Permission.DATA_READ
            },
            description="Read-only access for quality monitoring"
        ),
        "user": Role(
            name="user",
            permissions={
                Permission.CHATBOT_EXECUTE,
                Permission.DATA_READ
            },
            description="Basic chatbot access"
        )
    }
    
    def __init__(self, db_path: str = "rbac.db"):
        """Initialize RBAC framework with database"""
        self.db_path = db_path
        self._init_database()
        self._load_roles()
    
    def _init_database(self):
        """Initialize SQLite database for RBAC"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                role_id TEXT PRIMARY KEY,
                role_name TEXT UNIQUE NOT NULL,
                description TEXT,
                permissions TEXT
            )
        """)
        
        # User roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id TEXT,
                role_id TEXT,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (role_id) REFERENCES roles(role_id)
            )
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                resource TEXT,
                permission TEXT,
                result TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_roles(self):
        """Load predefined roles into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for role_name, role in self.ROLES.items():
            permissions_json = json.dumps([p.value for p in role.permissions])
            cursor.execute("""
                INSERT OR REPLACE INTO roles (role_id, role_name, description, permissions)
                VALUES (?, ?, ?, ?)
            """, (role_name, role.name, role.description, permissions_json))
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: str, username: str, email: Optional[str] = None) -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, username, email)
                VALUES (?, ?, ?)
            """, (user_id, username, email))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user"""
        if role_name not in self.ROLES:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO user_roles (user_id, role_id)
                VALUES (?, ?)
            """, (user_id, role_name))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all roles for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role_id FROM user_roles WHERE user_id = ?
        """, (user_id,))
        roles = [row[0] for row in cursor.fetchall()]
        conn.close()
        return roles
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user"""
        roles = self.get_user_roles(user_id)
        permissions = set()
        
        for role_name in roles:
            if role_name in self.ROLES:
                role = self.ROLES[role_name]
                permissions.update(role.permissions)
        
        # Admin has all permissions
        if Permission.ADMIN_ALL in permissions:
            permissions = set(Permission)
        
        return permissions
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        user_permissions = self.get_user_permissions(user_id)
        
        # Admin has all permissions
        if Permission.ADMIN_ALL in user_permissions:
            return True
        
        result = permission in user_permissions
        self._log_access(user_id, "check_permission", permission.value, result)
        return result
    
    def _log_access(self, user_id: str, action: str, resource: str, result: bool):
        """Log access attempt for audit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (user_id, action, resource, permission, result)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, resource, resource, "allowed" if result else "denied"))
        conn.commit()
        conn.close()
    
    def get_audit_log(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Retrieve audit log entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT * FROM audit_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
