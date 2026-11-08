
from security import (
    register_user,
    login_user,
    check_permission
)

print("\n===== SME SECURITY TESTING =====")

# Register system users
register_user(
    "admin",
    "Admin@2026Secure",
    "Administrator"
)

register_user(
    "manager",
    "Manager@2026Secure",
    "Manager"
)

register_user(
    "employee",
    "Employee@2026Secure",
    "Employee"
)

# Test administrator login
print("\n1. Administrator Login")
admin_role = login_user(
    "admin",
    "Admin@2026Secure"
)

# Test employee login
print("\n2. Employee Login")
employee_role = login_user(
    "employee",
    "Employee@2026Secure"
)

# Test access permissions
print("\n3. Administrator Access Test")
check_permission(admin_role, "manage_users")

print("\n4. Employee Access Test")
check_permission(employee_role, "manage_users")

print("\n5. Employee Customer Access Test")
check_permission(employee_role, "view_customers")
