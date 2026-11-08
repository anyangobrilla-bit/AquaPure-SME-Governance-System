
# ============================================================
# AQUAPURE WATER SOLUTIONS
# ENHANCED INCIDENT RESPONSE MANAGEMENT MODULE
# AUTOMATIC AUDIT LOGGING
# ============================================================

from database import connect_db
from audit import log_action


# ============================================================
# 1. CREATE INCIDENT ACTION HISTORY TABLE
# ============================================================

def create_incident_action_table():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incident_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                action_taken TEXT NOT NULL,
                recorded_by TEXT NOT NULL,
                action_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES incidents(id)
            )
        """)

        conn.commit()

        print("Incident action history table is ready.")

    finally:
        conn.close()


# ============================================================
# 2. REPORT A NEW SECURITY INCIDENT
# ============================================================

def report_incident(
    incident_type,
    description,
    severity,
    reported_by="admin"
):

    allowed_severities = [
        "Low", "Medium", "High", "Critical"
    ]

    if not all(
        isinstance(value, str)
        for value in [incident_type, description, severity, reported_by]
    ):
        print("Invalid input. All fields must contain text.")
        return None

    incident_type = incident_type.strip()
    description = description.strip()
    severity = severity.strip().capitalize()
    reported_by = reported_by.strip()

    if not incident_type or not description or not reported_by:
        print("Incident type, description and username are required.")
        return None

    if severity not in allowed_severities:
        print("Invalid severity. Choose Low, Medium, High or Critical.")
        return None

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO incidents
            (incident_type, description, severity, status)
            VALUES (?, ?, ?, 'OPEN')
        """, (incident_type, description, severity))

        incident_id = cursor.lastrowid

        conn.commit()

    finally:
        conn.close()

    log_action(
        reported_by,
        f"Reported incident ID {incident_id}: "
        f"{incident_type}. Severity: {severity}."
    )

    print("\nIncident recorded successfully.")
    print("Incident ID:", incident_id)
    print("Reported by:", reported_by)
    print("Severity:", severity)
    print("Status: OPEN")

    return incident_id


# ============================================================
# 3. UPDATE INCIDENT STATUS
# ============================================================

def update_incident_status(
    incident_id,
    new_status,
    updated_by="admin"
):

    allowed_statuses = [
        "OPEN",
        "INVESTIGATING",
        "RESOLVED"
    ]

    if not isinstance(new_status, str):
        print("Invalid status.")
        return False

    new_status = new_status.strip().upper()
    updated_by = str(updated_by).strip()

    if new_status not in allowed_statuses:
        print("Invalid status.")
        print("Choose OPEN, INVESTIGATING or RESOLVED.")
        return False

    if not updated_by:
        print("Username is required.")
        return False

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status
            FROM incidents
            WHERE id = ?
        """, (incident_id,))

        incident = cursor.fetchone()

        if incident is None:
            print("Incident ID not found.")
            return False

        old_status = incident[0]

        if old_status == new_status:
            print("Incident already has this status.")
            return False

        cursor.execute("""
            UPDATE incidents
            SET status = ?
            WHERE id = ?
        """, (new_status, incident_id))

        conn.commit()

    finally:
        conn.close()

    log_action(
        updated_by,
        f"Updated incident ID {incident_id} status "
        f"from {old_status} to {new_status}."
    )

    print("\nIncident status updated successfully.")
    print("Previous status:", old_status)
    print("New status:", new_status)

    return True


# ============================================================
# 4. RECORD INCIDENT RESPONSE ACTION
# ============================================================

def record_incident_action(
    incident_id,
    action_taken,
    recorded_by
):

    if not isinstance(action_taken, str):
        print("Invalid response action.")
        return False

    if not isinstance(recorded_by, str):
        print("Invalid username.")
        return False

    action_taken = action_taken.strip()
    recorded_by = recorded_by.strip()

    if not action_taken or not recorded_by:
        print("Action and staff username are required.")
        return False

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, status
            FROM incidents
            WHERE id = ?
        """, (incident_id,))

        incident = cursor.fetchone()

        if incident is None:
            print("Incident ID not found.")
            return False

        if incident[1] == "RESOLVED":
            print("Cannot add response actions to a resolved incident.")
            return False

        cursor.execute("""
            INSERT INTO incident_actions
            (incident_id, action_taken, recorded_by)
            VALUES (?, ?, ?)
        """, (incident_id, action_taken, recorded_by))

        conn.commit()

    finally:
        conn.close()

    log_action(
        recorded_by,
        f"Recorded response action for incident ID "
        f"{incident_id}: {action_taken}"
    )

    print("\nIncident response action recorded successfully.")

    return True


# ============================================================
# 5. VIEW ALL INCIDENTS AND RESPONSE ACTIONS
# ============================================================

def view_incidents():

    create_incident_action_table()

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                incident_type,
                description,
                severity,
                status
            FROM incidents
            ORDER BY id DESC
        """)

        incidents = cursor.fetchall()

        print("\n========== AQUAPURE INCIDENT REGISTER ==========")

        if not incidents:
            print("No incidents have been recorded.")
            return

        for incident in incidents:

            incident_id = incident[0]

            print("\nIncident ID:", incident[0])
            print("Incident Type:", incident[1])
            print("Description:", incident[2])
            print("Severity:", incident[3])
            print("Status:", incident[4])

            cursor.execute("""
                SELECT
                    action_taken,
                    recorded_by,
                    action_date
                FROM incident_actions
                WHERE incident_id = ?
                ORDER BY id
            """, (incident_id,))

            actions = cursor.fetchall()

            print("\nResponse Actions:")

            if actions:

                for action in actions:

                    print(" -", action[0])
                    print("   Recorded by:", action[1])
                    print("   Date:", action[2])

            else:

                print(" - No response actions recorded yet.")

            print("--------------------------------------------")

    finally:
        conn.close()


# ============================================================
# 6. RUN MODULE SAFELY
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("AQUAPURE INCIDENT RESPONSE MODULE")
    print("======================================")

    create_incident_action_table()

    view_incidents()

    print("\nIncident response module completed.")
