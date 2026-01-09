"""
Setup script for initializing the system
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rbac import RBACFramework
from src.semantic_store import SemanticStore


def setup_system():
    """Initialize system components"""
    print("Setting up Semantic Data Chatbot...")
    
    # Create directories
    databases_dir = Path("databases")
    databases_dir.mkdir(exist_ok=True)
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Initialize RBAC
    print("Initializing RBAC framework...")
    rbac = RBACFramework(db_path="databases/rbac.db")
    
    # Create default users
    print("Creating default users...")
    users = [
        ("admin", "admin", "admin@example.com", "admin"),
        ("operator1", "operator1", "operator1@example.com", "operator"),
        ("analyst1", "analyst1", "analyst1@example.com", "analyst"),
        ("user1", "user1", "user1@example.com", "user"),
    ]
    
    for user_id, username, email, role in users:
        try:
            rbac.create_user(user_id, username, email)
            rbac.assign_role(user_id, role)
            print(f"  Created user: {username} with role: {role}")
        except Exception as e:
            print(f"  User {username} might already exist: {e}")
    
    # Initialize semantic store
    print("Initializing semantic store...")
    try:
        store = SemanticStore(collection_name="semantic_data", persist_directory="databases/chroma_db")
        print("  Semantic store initialized")
    except Exception as e:
        print(f"  Warning: Could not initialize semantic store: {e}")
    
    print("\nSetup complete!")
    print("\nDefault users created:")
    print("  - admin (admin role)")
    print("  - operator1 (operator role)")
    print("  - analyst1 (analyst role)")
    print("  - user1 (user role)")


if __name__ == "__main__":
    setup_system()
