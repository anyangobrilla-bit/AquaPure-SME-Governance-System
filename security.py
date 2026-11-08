
# ============================================================
# AQUAPURE WATER SOLUTIONS
# SME GOVERNANCE AND CYBERSECURITY SYSTEM
# SECURITY AND ACCESS CONTROL MODULE
# ============================================================

import hashlib
import secrets

from database import connect_db
from audit import log_action


# ============================================================
# 1. PASSWORD HASHING
# ============================================================

def hash_password(password):

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600000
    ).hex()

    return salt + "$" + password_hash


def verify_password(password, stored_hash):

    try:
        salt, original_hash = stored_hash.split("$")

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            600000
        ).hex()

        return secrets.compare_digest(
            password_hash,
            original_hash
        )

    except (ValueError, AttributeError):
        return False


# ============================================================
# 2. USER REGISTRATION
# ============================================================

def register_user(username, password, role):

    allowed_roles = [
        "Administrator",
        "Manager",
        "Data Steward",
        "Employee"
    ]

    username = username.strip()
    role = role.strip()

    if not username or not password:
        print("Username and password are required.")
        return

    if role not in allowed_roles:
        print("Invalid user role.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    if cursor.fetchone():
        conn.close()
        print("Username already exists.")
        return

    password_hash = hash_password(password)

    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    """, (username, password_hash, role))

    conn.commit()
    conn.close()

    log_action(
        username,
        f"Registered new user with role: {role}"
    )

    print("User registered successfully.")
    print("Username:", username)
    print("Role:", role)


# ============================================================
# 3. USER LOGIN AUTHENTICATION
# ============================================================

def login_user(username, password):

    username = username.strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT password_hash, role
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[0]):

        role = user[1]

        log_action(
            username,
            "Successful login"
        )

        print("Login successful. Welcome", username + "!")
        print("Role:", role)

        return role

    log_action(
        username or "UNKNOWN",
        "Failed login attempt"
    )

    print("Invalid username or password.")

    return None


# ============================================================
# 4. ROLE-BASED PERMISSIONS
# ============================================================

def check_permission(role, action):

    permissions = {

        "Administrator": [
            "manage_users",
            "view_customers",
            "manage_customers",
            "view_risks",
            "manage_risks",
            "view_incidents",
            "manage_incidents",
            "view_audit",
            "view_governance",
            "view_compliance",
            "view_governance_monitor"
        ],

        "Manager": [
            "view_customers",
            "view_risks",
            "manage_risks",
            "view_incidents",
            "manage_incidents",
            "view_audit",
            "view_governance",
            "view_compliance"
        ],

        "Data Steward": [
            "view_customers",
            "manage_customers",
            "view_governance",
            "view_compliance"
        ],

        "Employee": [
            "view_customers",
            "view_governance"
        ]
    }

    if role in permissions and action in permissions[role]:
        return True

    print("ACCESS DENIED")
    print("Role:", role)
    print("Requested action:", action)

    log_action(
        role or "UNKNOWN",
        f"Denied permission: {action}"
    )

    return False


# ============================================================
# 5. DATA CLASSIFICATION ACCESS CONTROL
# ============================================================

def check_classification_access(role, classification):

    allowed_classifications = {

        "Administrator": [
            "PUBLIC",
            "INTERNAL",
            "CONFIDENTIAL",
            "RESTRICTED"
        ],

        "Manager": [
            "PUBLIC",
            "INTERNAL",
            "CONFIDENTIAL"
        ],

        "Data Steward": [
            "PUBLIC",
            "INTERNAL",
            "CONFIDENTIAL"
        ],

        "Employee": [
            "PUBLIC",
            "INTERNAL"
        ]
    }

    classification = classification.strip().upper()

    valid_classifications = [
        "PUBLIC",
        "INTERNAL",
        "CONFIDENTIAL",
        "RESTRICTED"
    ]

    if classification not in valid_classifications:

        print("ACCESS DENIED: Invalid data classification.")
        return False

    if (
        role in allowed_classifications
        and classification in allowed_classifications[role]
    ):

        print(
            f"ACCESS GRANTED: {role} can access "
            f"{classification} data."
        )

        return True

    print(
        f"ACCESS DENIED: {role} cannot access "
        f"{classification} data."
    )

    log_action(
        role or "UNKNOWN",
        f"Denied access to {classification} data"
    )

    return False


# ============================================================
# 6. SECURITY MODULE TEST
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("AQUAPURE SECURITY MODULE")
    print("======================================")

    print("\nTesting role-based permissions:")

    check_permission("Administrator", "manage_users")
    check_permission("Employee", "view_governance")

    print("\nTesting governance monitor permissions:")

    check_permission(
        "Administrator",
        "view_governance_monitor"
    )

    check_permission(
        "Employee",
        "view_governance_monitor"
    )

    print("\nTesting classification access:")

    check_classification_access(
        "Administrator", "RESTRICTED"
    )

    check_classification_access(
        "Manager", "CONFIDENTIAL"
    )

    check_classification_access(
        "Employee", "INTERNAL"
    )

    check_classification_access(
        "Employee", "RESTRICTED"
    )

    print("\nSecurity module test completed.")
