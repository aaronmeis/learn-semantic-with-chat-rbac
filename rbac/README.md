# RBAC Framework Documentation

## Overview

The Role-Based Access Control (RBAC) framework provides a comprehensive permission management system for the Semantic Data Chatbot. It implements a role-based model where users are assigned roles, and roles contain sets of permissions. This allows for fine-grained access control across all system components.

## Table of Contents

- [Architecture](#architecture)
- [Permissions](#permissions)
- [Roles](#roles)
- [User Management](#user-management)
- [Role Assignment](#role-assignment)
- [Permission Checking](#permission-checking)
- [Audit Logging](#audit-logging)
- [Decorators](#decorators)
- [Database Schema](#database-schema)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

## Architecture

The RBAC framework consists of several key components:

```
RBACFramework
├── Permission (Enum) - Defines all system permissions
├── Role (Dataclass) - Defines roles with permission sets
├── User Management - Create and manage users
├── Role Assignment - Assign roles to users
├── Permission Checking - Verify user permissions
└── Audit Logging - Track all access attempts
```

### Core Components

- **`framework.py`** - Main RBAC implementation with database backend
- **`decorators.py`** - Decorators for function-level permission checks
- **`models.py`** - Data models (User, RoleAssignment)

## Permissions

The system defines 9 distinct permissions:

### 1. `CHATBOT_EXECUTE` (`chatbot:execute`)
- **Purpose**: Execute chatbot queries and generate responses
- **Required by**: RunningAgent
- **Used for**: Main chatbot functionality

### 2. `VALIDATION_EXECUTE` (`validation:execute`)
- **Purpose**: Execute validation checks on chatbot responses
- **Required by**: ValidationAgent
- **Used for**: Response validation and quality assurance

### 3. `QUALITY_MONITOR` (`quality:monitor`)
- **Purpose**: Monitor and record quality metrics
- **Required by**: QualityAgent
- **Used for**: Tracking interaction quality

### 4. `QUALITY_ANALYZE` (`quality:analyze`)
- **Purpose**: Analyze quality metrics and generate reports
- **Required by**: QualityAgent
- **Used for**: Quality analysis and reporting

### 5. `DATA_READ` (`data:read`)
- **Purpose**: Read data from semantic store and databases
- **Required by**: All agents
- **Used for**: Accessing stored information

### 6. `DATA_WRITE` (`data:write`)
- **Purpose**: Write data to databases and stores
- **Required by**: QualityAgent
- **Used for**: Storing metrics and interactions

### 7. `POLICY_READ` (`policy:read`)
- **Purpose**: Read validation and system policies
- **Required by**: ValidationAgent
- **Used for**: Policy-based validation

### 8. `POLICY_WRITE` (`policy:write`)
- **Purpose**: Modify system policies
- **Required by**: Admin operations
- **Used for**: Policy management

### 9. `ADMIN_ALL` (`admin:all`)
- **Purpose**: Full system access (grants all permissions)
- **Required by**: Admin users
- **Used for**: Complete system control

## Roles

Roles are predefined collections of permissions. Users can have multiple roles, and permissions are combined from all assigned roles.

### Admin Role
```python
{
    "name": "admin",
    "permissions": {Permission.ADMIN_ALL},
    "description": "Full system access"
}
```
- **Permissions**: All 9 permissions (via ADMIN_ALL)
- **Use Case**: System administrators, full control

### Operator Role
```python
{
    "name": "operator",
    "permissions": {
        Permission.CHATBOT_EXECUTE,
        Permission.VALIDATION_EXECUTE,
        Permission.DATA_READ
    },
    "description": "Can execute and validate chatbot operations"
}
```
- **Permissions**: 3 permissions
- **Use Case**: Operators who can run and validate chatbot queries

### Analyst Role
```python
{
    "name": "analyst",
    "permissions": {
        Permission.QUALITY_MONITOR,
        Permission.QUALITY_ANALYZE,
        Permission.DATA_READ
    },
    "description": "Read-only access for quality monitoring"
}
```
- **Permissions**: 3 permissions
- **Use Case**: Quality analysts who monitor system performance

### User Role
```python
{
    "name": "user",
    "permissions": {
        Permission.CHATBOT_EXECUTE,
        Permission.DATA_READ
    },
    "description": "Basic chatbot access"
}
```
- **Permissions**: 2 permissions
- **Use Case**: Regular users with basic chatbot access

## User Management

### Creating Users

```python
from src.rbac import RBACFramework

rbac = RBACFramework(db_path="databases/rbac.db")

# Create a new user
success = rbac.create_user(
    user_id="john_doe",
    username="john_doe",
    email="john@example.com"
)

if success:
    print("User created successfully")
else:
    print("User already exists or creation failed")
```

**Parameters:**
- `user_id` (str): Unique identifier for the user
- `username` (str): Human-readable username (must be unique)
- `email` (str, optional): User's email address

**Returns:** `bool` - True if user was created, False if user already exists

### Getting User Roles

```python
roles = rbac.get_user_roles("john_doe")
print(f"User roles: {roles}")  # ['operator', 'user']
```

**Returns:** `List[str]` - List of role names assigned to the user

### Getting User Permissions

```python
permissions = rbac.get_user_permissions("john_doe")
print(f"User has {len(permissions)} permissions")
for perm in permissions:
    print(f"  - {perm.value}")
```

**Returns:** `Set[Permission]` - Set of all permissions the user has

**Note:** If a user has the `ADMIN_ALL` permission, this method returns all available permissions.

## Role Assignment

### Assigning Roles

```python
# Assign a role to a user
success = rbac.assign_role("john_doe", "operator")

if success:
    print("Role assigned successfully")
else:
    print("Role assignment failed (invalid role or user doesn't exist)")
```

**Parameters:**
- `user_id` (str): User identifier
- `role_name` (str): Name of the role to assign (must be one of: "admin", "operator", "analyst", "user")

**Returns:** `bool` - True if role was assigned, False otherwise

**Important:** Users can have multiple roles. Permissions are combined from all roles.

### Example: Granting Validation Permission

To fix the validation agent error, grant the `operator` role:

```python
rbac.assign_role("user1", "operator")
```

This grants:
- `chatbot:execute`
- `validation:execute` ← Fixes validation agent
- `data:read`

## Permission Checking

### Checking a Single Permission

```python
from src.rbac import RBACFramework, Permission

rbac = RBACFramework(db_path="databases/rbac.db")

# Check if user has a specific permission
has_permission = rbac.check_permission("john_doe", Permission.VALIDATION_EXECUTE)

if has_permission:
    print("User can execute validation")
else:
    print("Permission denied")
```

**Parameters:**
- `user_id` (str): User identifier
- `permission` (Permission): Permission enum value to check

**Returns:** `bool` - True if user has permission, False otherwise

**Note:** This method automatically logs the access attempt to the audit log.

### Admin Permission Handling

Users with `ADMIN_ALL` permission automatically have all permissions:

```python
# Admin user always returns True for any permission check
rbac.check_permission("admin", Permission.VALIDATION_EXECUTE)  # True
rbac.check_permission("admin", Permission.DATA_WRITE)          # True
rbac.check_permission("admin", Permission.QUALITY_ANALYZE)     # True
```

## Audit Logging

All permission checks are automatically logged for audit purposes.

### Retrieving Audit Logs

```python
# Get all recent audit logs
logs = rbac.get_audit_log(limit=100)

# Get audit logs for a specific user
user_logs = rbac.get_audit_log(user_id="john_doe", limit=50)

for log in logs:
    print(f"{log['timestamp']}: {log['user_id']} - {log['permission']} - {log['result']}")
```

**Parameters:**
- `user_id` (str, optional): Filter by specific user
- `limit` (int): Maximum number of entries to return (default: 100)

**Returns:** `List[Dict]` - List of audit log entries

### Audit Log Structure

Each audit log entry contains:
- `log_id`: Unique log identifier
- `user_id`: User who attempted access
- `action`: Action performed (e.g., "check_permission")
- `resource`: Resource accessed
- `permission`: Permission checked
- `result`: "allowed" or "denied"
- `timestamp`: When the check occurred

## Decorators

The framework provides decorators for function-level permission checking.

### Using `@require_permission`

```python
from src.rbac.decorators import require_permission, set_rbac_instance
from src.rbac import Permission, RBACFramework

# Initialize RBAC and set global instance
rbac = RBACFramework(db_path="databases/rbac.db")
set_rbac_instance(rbac)

@require_permission(Permission.VALIDATION_EXECUTE)
def validate_response(response: str, user_id: str):
    """This function requires validation:execute permission"""
    # Validation logic here
    return {"is_valid": True}

# Usage
try:
    result = validate_response("Response text", user_id="operator1")
except PermissionError as e:
    print(f"Permission denied: {e}")
```

### Using `@require_role`

```python
from src.rbac.decorators import require_role

@require_role("admin")
def admin_function(user_id: str):
    """This function requires admin role"""
    # Admin-only logic here
    pass
```

**Note:** Decorators require the global RBAC instance to be set using `set_rbac_instance()`.

## Database Schema

The RBAC framework uses SQLite with the following tables:

### Users Table
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
```

### Roles Table
```sql
CREATE TABLE roles (
    role_id TEXT PRIMARY KEY,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT  -- JSON array of permission strings
)
```

### User Roles Table
```sql
CREATE TABLE user_roles (
    user_id TEXT,
    role_id TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
)
```

### Audit Log Table
```sql
CREATE TABLE audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT,
    resource TEXT,
    permission TEXT,
    result TEXT,  -- "allowed" or "denied"
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Usage Examples

### Complete User Setup

```python
from src.rbac import RBACFramework, Permission

rbac = RBACFramework(db_path="databases/rbac.db")

# 1. Create user
rbac.create_user("new_user", "new_user", "new_user@example.com")

# 2. Assign role
rbac.assign_role("new_user", "operator")

# 3. Verify permissions
permissions = rbac.get_user_permissions("new_user")
print(f"User has {len(permissions)} permissions:")
for perm in permissions:
    print(f"  - {perm.value}")

# 4. Check specific permission
can_validate = rbac.check_permission("new_user", Permission.VALIDATION_EXECUTE)
print(f"Can validate: {can_validate}")  # True
```

### Granting Multiple Roles

```python
# Users can have multiple roles - permissions are combined
rbac.assign_role("user1", "user")      # Basic access
rbac.assign_role("user1", "analyst")  # Add quality monitoring

# Now user1 has permissions from both roles:
# - chatbot:execute (from user)
# - data:read (from user)
# - quality:monitor (from analyst)
# - quality:analyze (from analyst)
```

### Checking Permissions Before Operations

```python
def execute_validation(user_id: str, response: str):
    rbac = RBACFramework(db_path="databases/rbac.db")
    
    # Check permission before executing
    if not rbac.check_permission(user_id, Permission.VALIDATION_EXECUTE):
        raise PermissionError(f"User {user_id} cannot execute validation")
    
    # Proceed with validation
    # ... validation logic ...
```

### Using Command-Line Script

A helper script is available for quick permission management:

```bash
# Grant operator role (includes validation:execute)
python3 grant_permissions.py user1 operator

# Grant admin role (all permissions)
python3 grant_permissions.py user1 admin

# Grant analyst role (quality monitoring)
python3 grant_permissions.py user1 analyst
```

## Best Practices

### 1. Always Check Permissions
- Use `check_permission()` or `require_permission()` before sensitive operations
- Don't rely on UI-level checks alone - enforce at the code level

### 2. Use Roles, Not Direct Permissions
- Assign roles to users, not individual permissions
- Roles make permission management easier and more maintainable

### 3. Audit Logging
- All permission checks are automatically logged
- Review audit logs regularly for security monitoring
- Use `get_audit_log()` to track access patterns

### 4. Admin Permissions
- Users with `ADMIN_ALL` automatically have all permissions
- Use admin role sparingly - prefer specific roles when possible

### 5. Multiple Roles
- Users can have multiple roles
- Permissions are combined (union) from all roles
- Useful for users who need capabilities from different roles

### 6. Error Handling
- Always handle `PermissionError` exceptions
- Provide clear error messages to users
- Log permission denials for security review

### 7. Database Path
- Use consistent database paths across your application
- Default is `rbac.db` in current directory
- Recommended: `databases/rbac.db` for better organization

## Integration with Agents

All agents use the RBAC framework for permission checking:

### RunningAgent
- Requires: `CHATBOT_EXECUTE`, `DATA_READ`
- Checks permissions before executing queries

### ValidationAgent
- Requires: `VALIDATION_EXECUTE`, `DATA_READ`, `POLICY_READ`
- Checks permissions before validating responses

### QualityAgent
- Requires: `QUALITY_MONITOR`, `DATA_WRITE` (for execute)
- Requires: `QUALITY_ANALYZE`, `DATA_READ` (for analyze_quality)

## Troubleshooting

### Permission Denied Errors

**Problem:** User getting permission denied errors

**Solution:**
```python
# Check user's current roles
roles = rbac.get_user_roles("user1")
print(f"Current roles: {roles}")

# Check user's permissions
perms = rbac.get_user_permissions("user1")
print(f"Current permissions: {[p.value for p in perms]}")

# Grant appropriate role
rbac.assign_role("user1", "operator")  # For validation
# OR
rbac.assign_role("user1", "admin")     # For all permissions
```

### User Not Found

**Problem:** `get_user_roles()` returns empty list

**Solution:**
```python
# Ensure user exists
rbac.create_user("user1", "user1", "user1@example.com")

# Then assign role
rbac.assign_role("user1", "operator")
```

### Database Not Found

**Problem:** Database file doesn't exist

**Solution:**
- The framework automatically creates the database on initialization
- Ensure the directory exists: `mkdir -p databases`
- Initialize: `rbac = RBACFramework(db_path="databases/rbac.db")`

## API Reference

### RBACFramework Class

#### `__init__(db_path: str = "rbac.db")`
Initialize RBAC framework with database path.

#### `create_user(user_id: str, username: str, email: Optional[str] = None) -> bool`
Create a new user in the system.

#### `assign_role(user_id: str, role_name: str) -> bool`
Assign a role to a user.

#### `get_user_roles(user_id: str) -> List[str]`
Get all roles assigned to a user.

#### `get_user_permissions(user_id: str) -> Set[Permission]`
Get all permissions for a user (from all their roles).

#### `check_permission(user_id: str, permission: Permission) -> bool`
Check if a user has a specific permission. Logs to audit log.

#### `get_audit_log(user_id: Optional[str] = None, limit: int = 100) -> List[Dict]`
Retrieve audit log entries.

## Related Documentation

- [Agents README](../agents/README.md) - How agents use RBAC
- [Main README](../../README.md) - Overall system documentation
- [Dashboard Guide](../../DASHBOARD_GUIDE.md) - Visual RBAC monitoring
