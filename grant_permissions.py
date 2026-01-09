#!/usr/bin/env python3
"""
Quick script to grant permissions to users by assigning roles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.rbac import RBACFramework, Permission

def main():
    """Grant permissions to users"""
    rbac = RBACFramework(db_path="databases/rbac.db")
    
    print("🔐 RBAC Permission Manager\n")
    print("Available Roles:")
    print("  1. admin - Full system access (all permissions)")
    print("  2. operator - Can execute and validate (chatbot:execute, validation:execute, data:read)")
    print("  3. analyst - Quality monitoring (quality:monitor, quality:analyze, data:read)")
    print("  4. user - Basic access (chatbot:execute, data:read)")
    print()
    
    # Show current users
    print("Current Users:")
    users = ["admin", "operator1", "user1"]
    for user_id in users:
        roles = rbac.get_user_roles(user_id)
        perms = rbac.get_user_permissions(user_id)
        print(f"  - {user_id}: roles={roles}, permissions={len(perms)}")
    print()
    
    # Interactive mode
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        role_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not role_name:
            print(f"Usage: python3 grant_permissions.py <user_id> <role_name>")
            print(f"Example: python3 grant_permissions.py user1 operator")
            return
        
        # Ensure user exists
        try:
            rbac.create_user(user_id, user_id, f"{user_id}@example.com")
        except:
            pass
        
        # Assign role
        if rbac.assign_role(user_id, role_name):
            print(f"✅ Successfully assigned role '{role_name}' to user '{user_id}'")
            roles = rbac.get_user_roles(user_id)
            perms = rbac.get_user_permissions(user_id)
            print(f"   User now has roles: {roles}")
            print(f"   User now has {len(perms)} permissions")
        else:
            print(f"❌ Failed to assign role. Make sure role '{role_name}' exists.")
    else:
        print("Usage: python3 grant_permissions.py <user_id> <role_name>")
        print("\nExamples:")
        print("  python3 grant_permissions.py user1 operator  # Grant validation:execute to user1")
        print("  python3 grant_permissions.py user1 admin     # Grant all permissions to user1")
        print("\nTo fix the validation agent error, run:")
        print("  python3 grant_permissions.py user1 operator")

if __name__ == "__main__":
    main()
