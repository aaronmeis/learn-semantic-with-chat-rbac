"""
Tests for RBAC Framework
"""

import pytest
import os
import tempfile
from pathlib import Path

from src.rbac import RBACFramework, Permission


@pytest.fixture
def rbac():
    """Create a temporary RBAC instance for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_rbac.db")
        yield RBACFramework(db_path=db_path)


def test_create_user(rbac):
    """Test user creation"""
    assert rbac.create_user("test_user", "testuser", "test@example.com")
    assert not rbac.create_user("test_user", "testuser", "test@example.com")  # Duplicate


def test_assign_role(rbac):
    """Test role assignment"""
    rbac.create_user("test_user", "testuser", "test@example.com")
    assert rbac.assign_role("test_user", "operator")
    assert rbac.assign_role("test_user", "admin")
    assert not rbac.assign_role("test_user", "invalid_role")


def test_get_user_roles(rbac):
    """Test getting user roles"""
    rbac.create_user("test_user", "testuser", "test@example.com")
    rbac.assign_role("test_user", "operator")
    rbac.assign_role("test_user", "analyst")
    
    roles = rbac.get_user_roles("test_user")
    assert "operator" in roles
    assert "analyst" in roles


def test_check_permission(rbac):
    """Test permission checking"""
    rbac.create_user("admin_user", "admin", "admin@example.com")
    rbac.assign_role("admin_user", "admin")
    
    rbac.create_user("user_user", "user", "user@example.com")
    rbac.assign_role("user_user", "user")
    
    # Admin should have all permissions
    assert rbac.check_permission("admin_user", Permission.CHATBOT_EXECUTE)
    assert rbac.check_permission("admin_user", Permission.DATA_WRITE)
    
    # User should have limited permissions
    assert rbac.check_permission("user_user", Permission.CHATBOT_EXECUTE)
    assert not rbac.check_permission("user_user", Permission.DATA_WRITE)


def test_get_user_permissions(rbac):
    """Test getting all user permissions"""
    rbac.create_user("operator_user", "operator", "op@example.com")
    rbac.assign_role("operator_user", "operator")
    
    permissions = rbac.get_user_permissions("operator_user")
    assert Permission.CHATBOT_EXECUTE in permissions
    assert Permission.VALIDATION_EXECUTE in permissions
    assert Permission.DATA_READ in permissions
    assert Permission.DATA_WRITE not in permissions


def test_audit_log(rbac):
    """Test audit logging"""
    rbac.create_user("test_user", "testuser", "test@example.com")
    rbac.assign_role("test_user", "user")
    
    # Check permission (should log)
    rbac.check_permission("test_user", Permission.CHATBOT_EXECUTE)
    
    # Get audit log
    logs = rbac.get_audit_log(user_id="test_user")
    assert len(logs) > 0
    assert logs[0]["user_id"] == "test_user"
    assert logs[0]["permission"] == Permission.CHATBOT_EXECUTE.value
