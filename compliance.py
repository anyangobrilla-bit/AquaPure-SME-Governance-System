
from database import connect_db
from audit import log_action
import pandas as pd


# ==========================================
# 1. CREATE COMPLIANCE TABLE
# ==========================================

def create_compliance_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            framework TEXT NOT NULL,
            control_code TEXT UNIQUE NOT NULL,
            requirement TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started',
            evidence TEXT,
            action_required TEXT,
            responsible_person TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# 2. ADD COMPLIANCE REQUIREMENT
# ==========================================

def add_compliance_check(
    framework,
    control_code,
    requirement,
    evidence,
    action_required,
    responsible_person
):

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO compliance_checks (
                framework,
                control_code,
                requirement,
                evidence,
                action_required,
                responsible_person
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            framework,
            control_code,
            requirement,
            evidence,
            action_required,
            responsible_person
        ))

        conn.commit()

        print("Compliance requirement added successfully.")

        log_action(
            "admin",
            f"Added compliance requirement: {control_code}"
        )

    except Exception as error:

        print("Could not add requirement:", error)

    finally:

        conn.close()


# ==========================================
# 3. UPDATE COMPLIANCE STATUS
# ==========================================

def update_compliance_status(control_code, new_status):

    allowed_statuses = [
        "Not Started",
        "In Progress",
        "Implemented",
        "Needs Review"
    ]

    if new_status not in allowed_statuses:

        print("Invalid compliance status.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status
        FROM compliance_checks
        WHERE control_code = ?
    """, (control_code,))

    result = cursor.fetchone()

    if result is None:

        conn.close()
        print("Compliance requirement not found.")
        return

    old_status = result[0]

    cursor.execute("""
        UPDATE compliance_checks
        SET status = ?
        WHERE control_code = ?
    """, (new_status, control_code))

    conn.commit()
    conn.close()

    print("Compliance status updated successfully.")

    log_action(
        "admin",
        f"Updated compliance {control_code}: "
        f"{old_status} to {new_status}"
    )


# ==========================================
# 4. UPDATE COMPLIANCE EVIDENCE
# ==========================================

def update_compliance_evidence(
    control_code,
    evidence,
    action_required,
    responsible_person
):

    if not all([
        control_code,
        evidence,
        action_required,
        responsible_person
    ]):

        print("All fields are required.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT control_code
        FROM compliance_checks
        WHERE control_code = ?
    """, (control_code,))

    result = cursor.fetchone()

    if result is None:

        conn.close()
        print("Compliance requirement not found.")
        return

    cursor.execute("""
        UPDATE compliance_checks
        SET evidence = ?,
            action_required = ?,
            responsible_person = ?
        WHERE control_code = ?
    """, (
        evidence,
        action_required,
        responsible_person,
        control_code
    ))

    conn.commit()
    conn.close()

    print("Compliance evidence details updated successfully.")

    log_action(
        "admin",
        f"Updated evidence details for compliance {control_code}"
    )


# ==========================================
# 5. VIEW COMPLIANCE REGISTER
# ==========================================

def view_compliance_checks():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, framework, control_code, requirement,
               status, evidence, action_required,
               responsible_person
        FROM compliance_checks
        ORDER BY id
    """)

    records = cursor.fetchall()
    conn.close()

    print("\n========== AQUAPURE COMPLIANCE REGISTER ==========")

    if not records:

        print("No compliance requirements found.")
        return

    for record in records:

        print("\nRecord ID:", record[0])
        print("Framework:", record[1])
        print("Control Code:", record[2])
        print("Requirement:", record[3])
        print("Status:", record[4])
        print("Evidence:", record[5])
        print("Action Required:", record[6])
        print("Responsible Person:", record[7])

        print("----------------------------------------")


# ==========================================
# 6. COMPLIANCE SUMMARY
# ==========================================

def compliance_summary():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, COUNT(*)
        FROM compliance_checks
        GROUP BY status
    """)

    results = cursor.fetchall()
    conn.close()

    status_counts = {
        "Not Started": 0,
        "In Progress": 0,
        "Implemented": 0,
        "Needs Review": 0
    }

    for status, count in results:

        status_counts[status] = count

    total = sum(status_counts.values())

    implemented = status_counts["Implemented"]

    if total > 0:

        progress = (implemented / total) * 100

    else:

        progress = 0

    print("\n========== COMPLIANCE SUMMARY ==========")

    print("Total Requirements:", total)

    print("Implemented:", status_counts["Implemented"])

    print("In Progress:", status_counts["In Progress"])

    print("Not Started:", status_counts["Not Started"])

    print("Needs Review:", status_counts["Needs Review"])

    print("----------------------------------------")

    print("Implementation Progress: {:.2f}%".format(progress))

    print("----------------------------------------")


# ==========================================
# 7. EXPORT COMPLIANCE REPORT TO EXCEL
# ==========================================

def export_compliance_report(filename="compliance_report.xlsx"):

    conn = connect_db()

    query = """
        SELECT framework, control_code, requirement, status,
               evidence, action_required, responsible_person
        FROM compliance_checks
        ORDER BY framework, control_code
    """

    dataframe = pd.read_sql_query(query, conn)

    conn.close()

    dataframe.to_excel(filename, index=False)

    print("\nCompliance report exported successfully.")

    print("File:", filename)

    print("Total requirements exported:", len(dataframe))


# ==========================================
# 8. INITIALIZE EXISTING REQUIREMENTS
# ==========================================

def initialize_compliance_system():

    create_compliance_table()

    requirements = [

        (
            "Kenya Data Protection Act, 2019",
            "DPA-01",
            "Protect personal data against unauthorized access.",
            "User authentication and role-based access controls.",
            "Review user permissions regularly.",
            "System Administrator"
        ),

        (
            "Kenya Data Protection Act, 2019",
            "DPA-02",
            "Ensure personal data is collected for specified purposes.",
            "Customer data collection records.",
            "Document the purpose of each data collection activity.",
            "Data Protection Officer"
        ),

        (
            "Kenya Data Protection Act, 2019",
            "DPA-03",
            "Protect personal records from loss or unauthorized disclosure.",
            "Database access controls and locked filing cabinets.",
            "Review physical and electronic security measures.",
            "Data Steward"
        ),

        (
            "ISO/IEC 27001:2022",
            "ISO-01",
            "Control access to information and systems.",
            "User accounts and role-based permissions.",
            "Review access rights and remove unnecessary access.",
            "System Administrator"
        ),

        (
            "ISO/IEC 27001:2022",
            "ISO-02",
            "Maintain information security incident records.",
            "Incident register and audit logs.",
            "Review incident records regularly.",
            "Security Manager"
        ),

        (
            "ISO/IEC 27001:2022",
            "ISO-03",
            "Maintain backups and protect information against data loss.",
            "Database backup procedures.",
            "Test backup restoration periodically.",
            "System Administrator"
        )
    ]

    for requirement in requirements:

        add_compliance_check(*requirement)


# ==========================================
# 9. RUN MODULE DIRECTLY
# ==========================================

if __name__ == "__main__":

    print("\n===== AQUAPURE COMPLIANCE MANAGEMENT SYSTEM =====")

    initialize_compliance_system()

    view_compliance_checks()

    compliance_summary()
