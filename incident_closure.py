
# ============================================================
# AQUAPURE WATER SOLUTIONS
# INCIDENT CLOSURE AND EVIDENCE MANAGEMENT MODULE
# ============================================================

from database import connect_db
from audit import log_action
from datetime import datetime


# ------------------------------------------------------------
# 1. CREATE EVIDENCE AND INCIDENT CLOSURE TABLES
# ------------------------------------------------------------

def create_closure_tables():

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                evidence_type TEXT NOT NULL,
                evidence_reference TEXT NOT NULL,
                description TEXT NOT NULL,
                recorded_by TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (incident_id) REFERENCES incidents(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_closures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL UNIQUE,
                root_cause TEXT NOT NULL,
                corrective_action TEXT NOT NULL,
                preventive_action TEXT NOT NULL,
                closure_summary TEXT NOT NULL,
                closed_by TEXT NOT NULL,
                approved_by TEXT NOT NULL,
                closure_date TEXT NOT NULL,
                FOREIGN KEY (incident_id) REFERENCES incidents(id)
            )
        """)

        conn.commit()

        print("Incident evidence table created successfully.")
        print("Incident closure table created successfully.")

    finally:
        conn.close()


# ------------------------------------------------------------
# 2. RECORD INVESTIGATION EVIDENCE
# ------------------------------------------------------------

def record_evidence(
    incident_id,
    evidence_type,
    evidence_reference,
    description,
    recorded_by
):

    if not all([
        evidence_type.strip(),
        evidence_reference.strip(),
        description.strip(),
        recorded_by.strip()
    ]):
        print("All evidence fields are required.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, status FROM incidents WHERE id = ?",
            (incident_id,)
        )

        incident = cursor.fetchone()

        if incident is None:
            print("Incident not found.")
            return

        if incident[1] == "RESOLVED":
            print("Evidence cannot be added to a resolved incident.")
            return

        recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO incident_evidence (
                incident_id,
                evidence_type,
                evidence_reference,
                description,
                recorded_by,
                recorded_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            evidence_type.strip(),
            evidence_reference.strip(),
            description.strip(),
            recorded_by,
            recorded_at
        ))

        conn.commit()

        print("Investigation evidence recorded successfully.")

    finally:
        conn.close()

    log_action(
        recorded_by,
        f"Recorded evidence for incident ID {incident_id}: "
        f"{evidence_type}"
    )


# ------------------------------------------------------------
# 3. VIEW INVESTIGATION EVIDENCE
# ------------------------------------------------------------

def view_incident_evidence(incident_id=None):

    conn = connect_db()
    cursor = conn.cursor()

    try:
        if incident_id is None:
            cursor.execute("""
                SELECT id, incident_id, evidence_type,
                       evidence_reference, description,
                       recorded_by, recorded_at
                FROM incident_evidence
                ORDER BY id DESC
            """)
        else:
            cursor.execute("""
                SELECT id, incident_id, evidence_type,
                       evidence_reference, description,
                       recorded_by, recorded_at
                FROM incident_evidence
                WHERE incident_id = ?
                ORDER BY id DESC
            """, (incident_id,))

        records = cursor.fetchall()

        print("\n========================================")
        print("AQUAPURE INCIDENT INVESTIGATION EVIDENCE")
        print("========================================")

        if not records:
            print("No investigation evidence found.")
            return

        for record in records:
            print(f"\nEvidence ID: {record[0]}")
            print(f"Incident ID: {record[1]}")
            print(f"Evidence Type: {record[2]}")
            print(f"Evidence Reference: {record[3]}")
            print(f"Description: {record[4]}")
            print(f"Recorded By: {record[5]}")
            print(f"Recorded At: {record[6]}")
            print("----------------------------------------")

    finally:
        conn.close()


# ------------------------------------------------------------
# 4. FORMALLY CLOSE AN INCIDENT
# ------------------------------------------------------------

def close_incident(
    incident_id,
    root_cause,
    corrective_action,
    preventive_action,
    closure_summary,
    closed_by,
    approved_by
):

    required_fields = [
        root_cause,
        corrective_action,
        preventive_action,
        closure_summary,
        closed_by,
        approved_by
    ]

    if not all(field and field.strip() for field in required_fields):
        print("All incident closure fields are required.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, status FROM incidents WHERE id = ?",
            (incident_id,)
        )

        incident = cursor.fetchone()

        if incident is None:
            print("Incident not found.")
            return

        if incident[1] == "RESOLVED":
            print("This incident is already resolved.")
            return

        cursor.execute("""
            SELECT COUNT(*)
            FROM incident_evidence
            WHERE incident_id = ?
        """, (incident_id,))

        evidence_count = cursor.fetchone()[0]

        if evidence_count == 0:
            print(
                "Incident closure denied. "
                "Record investigation evidence first."
            )
            return

        closure_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO incident_closures (
                incident_id,
                root_cause,
                corrective_action,
                preventive_action,
                closure_summary,
                closed_by,
                approved_by,
                closure_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            root_cause.strip(),
            corrective_action.strip(),
            preventive_action.strip(),
            closure_summary.strip(),
            closed_by,
            approved_by,
            closure_date
        ))

        cursor.execute("""
            UPDATE incidents
            SET status = 'RESOLVED'
            WHERE id = ?
        """, (incident_id,))

        conn.commit()

        print("\nIncident formally closed successfully.")
        print(f"Incident ID: {incident_id}")
        print(f"Closed By: {closed_by}")
        print(f"Approved By: {approved_by}")
        print(f"Closure Date: {closure_date}")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    log_action(
        closed_by,
        f"Formally closed incident ID {incident_id}. "
        f"Approved by: {approved_by}."
    )


# ------------------------------------------------------------
# 5. VIEW FORMAL INCIDENT CLOSURE RECORDS
# ------------------------------------------------------------

def view_closure_records():

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                incident_id,
                root_cause,
                corrective_action,
                preventive_action,
                closure_summary,
                closed_by,
                approved_by,
                closure_date
            FROM incident_closures
            ORDER BY id DESC
        """)

        records = cursor.fetchall()

        print("\n========================================")
        print("AQUAPURE INCIDENT CLOSURE REGISTER")
        print("========================================")

        if not records:
            print("No formal incident closure records found.")
            return

        for record in records:
            print(f"\nIncident ID: {record[0]}")
            print(f"Root Cause: {record[1]}")
            print(f"Corrective Action: {record[2]}")
            print(f"Preventive Action: {record[3]}")
            print(f"Closure Summary: {record[4]}")
            print(f"Closed By: {record[5]}")
            print(f"Approved By: {record[6]}")
            print(f"Closure Date: {record[7]}")
            print("----------------------------------------")

    finally:
        conn.close()


# ------------------------------------------------------------
# 6. INITIALIZE MODULE WHEN RUN DIRECTLY
# ------------------------------------------------------------

if __name__ == "__main__":

    print("\n========================================")
    print("AQUAPURE INCIDENT CLOSURE MODULE")
    print("========================================")

    create_closure_tables()

    print("\nExisting investigation evidence:")
    view_incident_evidence()

    print("\nExisting formal closure records:")
    view_closure_records()

    print("\nIncident closure module initialized successfully.")
