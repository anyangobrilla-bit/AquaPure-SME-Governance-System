
# ============================================================
# AQUAPURE WATER SOLUTIONS
# SECURITY CONTROL VERIFICATION MODULE
# ============================================================

from security import check_permission, check_classification_access
from database import connect_db


# ============================================================
# 1. AUDIT LOG COUNT
# ============================================================

def get_audit_count():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM audit_logs
        """)

        result = cursor.fetchone()

        return result[0]

    finally:
        conn.close()


# ============================================================
# 2. TEST RESULT TRACKING
# ============================================================

test_results = []


def record_test(test_name, actual, expected):

    passed = actual == expected

    test_results.append({
        "name": test_name,
        "passed": passed
    })

    if passed:
        print(f"PASS: {test_name}")
    else:
        print(f"FAIL: {test_name}")
        print("Expected:", expected)
        print("Actual:", actual)


# ============================================================
# 3. ROLE-BASED PERMISSION TESTS
# ============================================================

def test_role_permissions():

    print("\n1. ROLE-BASED ACCESS CONTROL TESTS")
    print("-" * 50)

    tests = [

        (
            "Administrator can view governance monitor",
            "Administrator",
            "view_governance_monitor",
            True
        ),

        (
            "Administrator can view risks",
            "Administrator",
            "view_risks",
            True
        ),

        (
            "Manager can view risks",
            "Manager",
            "view_risks",
            True
        ),

        (
            "Manager cannot view governance monitor",
            "Manager",
            "view_governance_monitor",
            False
        ),

        (
            "Data Steward can view governance records",
            "Data Steward",
            "view_governance",
            True
        ),

        (
            "Employee can view governance records",
            "Employee",
            "view_governance",
            True
        ),

        (
            "Employee cannot view risks",
            "Employee",
            "view_risks",
            False
        ),

        (
            "Employee cannot view governance monitor",
            "Employee",
            "view_governance_monitor",
            False
        )

    ]

    for name, role, action, expected in tests:

        actual = check_permission(role, action)

        record_test(name, actual, expected)


# ============================================================
# 4. DATA CLASSIFICATION ACCESS TESTS
# ============================================================

def test_classification_permissions():

    print("\n2. DATA CLASSIFICATION ACCESS TESTS")
    print("-" * 50)

    tests = [

        (
            "Administrator can access RESTRICTED data",
            "Administrator",
            "RESTRICTED",
            True
        ),

        (
            "Manager can access CONFIDENTIAL data",
            "Manager",
            "CONFIDENTIAL",
            True
        ),

        (
            "Manager cannot access RESTRICTED data",
            "Manager",
            "RESTRICTED",
            False
        ),

        (
            "Data Steward can access CONFIDENTIAL data",
            "Data Steward",
            "CONFIDENTIAL",
            True
        ),

        (
            "Employee can access INTERNAL data",
            "Employee",
            "INTERNAL",
            True
        ),

        (
            "Employee cannot access CONFIDENTIAL data",
            "Employee",
            "CONFIDENTIAL",
            False
        ),

        (
            "Employee cannot access RESTRICTED data",
            "Employee",
            "RESTRICTED",
            False
        )

    ]

    for name, role, classification, expected in tests:

        actual = check_classification_access(
            role,
            classification
        )

        record_test(name, actual, expected)


# ============================================================
# 5. AUDIT LOGGING VERIFICATION
# ============================================================

def test_audit_logging(previous_count):

    print("\n3. AUDIT LOGGING VERIFICATION")
    print("-" * 50)

    current_count = get_audit_count()

    new_entries = current_count - previous_count

    print("Audit entries before tests:", previous_count)
    print("Audit entries after tests:", current_count)
    print("New audit entries:", new_entries)

    record_test(
        "Denied access attempts are recorded in audit logs",
        new_entries > 0,
        True
    )


# ============================================================
# 6. SECURITY VERIFICATION SUMMARY
# ============================================================

def display_summary():

    print("\n" + "=" * 55)
    print("AQUAPURE SECURITY VERIFICATION SUMMARY")
    print("=" * 55)

    total = len(test_results)

    passed = sum(
        1 for test in test_results
        if test["passed"]
    )

    failed = total - passed

    print("Total tests:", total)
    print("Tests passed:", passed)
    print("Tests failed:", failed)

    if failed == 0:

        print("\nRESULT: ALL SECURITY TESTS PASSED")

    else:

        print("\nRESULT: SOME SECURITY TESTS FAILED")

        print("\nTests requiring attention:")

        for test in test_results:

            if not test["passed"]:
                print("-", test["name"])

    print("=" * 55)


# ============================================================
# 7. RUN SECURITY VERIFICATION
# ============================================================

def run_security_verification():

    global test_results

    test_results = []

    print("\n" + "=" * 55)
    print("AQUAPURE SECURITY CONTROL VERIFICATION")
    print("=" * 55)

    previous_count = get_audit_count()

    test_role_permissions()

    test_classification_permissions()

    test_audit_logging(previous_count)

    display_summary()


# ============================================================
# 8. EXECUTE MODULE
# ============================================================

if __name__ == "__main__":

    run_security_verification()
