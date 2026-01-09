"""
Quick demo script to generate sample data for the dashboard
Run this before starting the dashboard to populate with demo data
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.monitoring import EventTracker
from src.rbac import RBACFramework
from src.rbac.framework import Permission


def generate_demo_data():
    """Generate sample data for dashboard demonstration"""
    
    print("Generating demo data for dashboard...")
    
    # Initialize tracker
    tracker = EventTracker(db_path="monitoring.db")
    
    # Initialize RBAC
    rbac = RBACFramework(db_path="databases/rbac.db")
    
    # Create demo users
    users = [
        ("admin", "admin"),
        ("operator1", "operator"),
        ("user1", "user")
    ]
    
    for user_id, role in users:
        try:
            rbac.create_user(user_id, user_id, f"{user_id}@example.com")
            rbac.assign_role(user_id, role)
        except:
            pass
    
    # Generate agent call events
    agents = [
        ("running_001", "RunningAgent"),
        ("validation_001", "ValidationAgent"),
        ("quality_001", "QualityAgent")
    ]
    
    print("Generating agent call events...")
    for i in range(30):
        agent_id, agent_name = agents[i % len(agents)]
        user_id = users[i % len(users)][0]
        
        tracker.track_agent_call(
            agent_id=agent_id,
            agent_name=agent_name,
            user_id=user_id,
            action="execute" if agent_name == "RunningAgent" else ("validate" if agent_name == "ValidationAgent" else "track_quality"),
            status="success" if i % 5 != 0 else "error",
            duration_ms=100 + (i * 10) + (i % 20),
            metadata={"demo": True, "iteration": i}
        )
        
        # Add some time variation
        time.sleep(0.1)
    
    # Generate RBAC check events for all permissions
    from src.rbac.framework import Permission
    
    # Get all permission values
    all_permissions = [p.value for p in Permission]
    
    print("Generating RBAC check events...")
    
    # For admin, check ALL permissions to show comprehensive view
    admin_user = "admin"
    for perm_value in all_permissions:
        try:
            perm_enum = Permission(perm_value)
            result = rbac.check_permission(admin_user, perm_enum)
            tracker.track_rbac_check(
                user_id=admin_user,
                agent_id="demo_agent",
                permission=perm_value,
                result=result,
                context=f"Admin permission check: {perm_value}"
            )
        except (ValueError, KeyError):
            pass
    
    # Generate additional checks for other users
    for i in range(30):
        user_id = users[i % len(users)][0]
        agent_id = agents[i % len(agents)][0]
        permission = all_permissions[i % len(all_permissions)]
        
        # Check if user actually has permission
        try:
            perm_enum = Permission(permission)
            result = rbac.check_permission(user_id, perm_enum)
        except (ValueError, KeyError):
            result = False
        
        tracker.track_rbac_check(
            user_id=user_id,
            agent_id=agent_id,
            permission=permission,
            result=result,
            context=f"Demo check {i}"
        )
        
        time.sleep(0.02)
    
    total_rbac_checks = len(all_permissions) + 30  # All perms for admin + 30 more
    print("✅ Demo data generated successfully!")
    print(f"   - {30} agent call events")
    print(f"   - {total_rbac_checks} RBAC check events ({len(all_permissions)} for admin, 30 for other users)")
    print(f"   - Admin has all {len(all_permissions)} permissions checked")
    print("\nYou can now start the dashboard with: streamlit run dashboard.py")


if __name__ == "__main__":
    generate_demo_data()
