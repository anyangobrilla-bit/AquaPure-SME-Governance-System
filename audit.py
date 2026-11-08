
# ============================================================
# AQUAPURE WATER SOLUTIONS
# ENHANCED AUDIT LOGGING AND MONITORING MODULE
# ============================================================

from database import connect_db
import pandas as pd
import sqlite3


# ============================================================
# 1. PROTECT AUDIT RECORDS FROM UPDATE AND DELETION
# ============================================================

def create_audit_protection():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_audit_update
            BEFORE UPDATE ON audit_logs
            BEGIN
                SELECT RAISE(
                    ABORT,
                    'Audit records cannot be modified.'
                );
            END;
        """)

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_audit_delete
            BEFORE DELETE ON audit_logs
            BEGIN
                SELECT RAISE(
                    ABORT,
                    'Audit records cannot be deleted.'
                );
            END;
        """)

        conn.commit()

        return True

    finally:
        conn.close()


# ============================================================
# 2. RECORD USER ACTIVITIES
# ============================================================

def log_action(username, action):

    if not isinstance(username, str) or not username.strip():
        print("Invalid username. Audit activity not recorded.")
        return False

    if not isinstance(action, str) or not action.strip():
        print("Invalid activity description.")
        return False

    conn = None

    try:

        create_audit_protection()

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_logs (username, action)
            VALUES (?, ?)
        """, (username.strip(), action.strip()))

        conn.commit()

        print("Audit activity recorded successfully.")

        return True

    except sqlite3.Error as error:

        if conn:
            conn.rollback()

        print("Audit logging error:", error)

        return False

    finally:

        if conn:
            conn.close()


# ============================================================
# 3. VIEW AUDIT RECORDS
# ============================================================

def view_audit_logs():

    conn = connect_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, action, timestamp
            FROM audit_logs
            ORDER BY id DESC
        """)

        logs = cursor.fetchall()

        print("\n========== AQUAPURE AUDIT LOGS ==========")

        if not logs:
            print("No audit records found.")
            return

        print("Total audit records:", len(logs))

        for log in logs:

            print("\nLog ID:", log[0])
            print("Username:", log[1])
            print("Action:", log[2])
            print("Timestamp:", log[3])
            print("----------------------------------------")

    finally:

        conn.close()


# ============================================================
# 4. EXPORT AUDIT RECORDS TO EXCEL
# ============================================================

def export_audit_logs(filename="audit_report.xlsx"):

    conn = connect_db()

    try:

        query = """
            SELECT id, username, action, timestamp
            FROM audit_logs
            ORDER BY id DESC
        """

        dataframe = pd.read_sql_query(query, conn)

        dataframe.to_excel(filename, index=False)

        print("\nAudit report exported successfully.")
        print("File:", filename)
        print("Total records exported:", len(dataframe))

    except Exception as error:

        print("Audit export failed:", error)

    finally:

        conn.close()


# ============================================================
# 5. CHECK AUDIT PROTECTION STATUS
# ============================================================

def check_audit_protection():

    conn = connect_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'trigger'
            AND name IN (
                'prevent_audit_update',
                'prevent_audit_delete'
            )
        """)

        triggers = [row[0] for row in cursor.fetchall()]

        print("\n===== AUDIT SECURITY STATUS =====")

        if "prevent_audit_update" in triggers:
            print("PASS: Audit update protection is active.")
        else:
            print("WARNING: Audit update protection is missing.")

        if "prevent_audit_delete" in triggers:
            print("PASS: Audit deletion protection is active.")
        else:
            print("WARNING: Audit deletion protection is missing.")

        print("Protection triggers found:", len(triggers), "/ 2")

        return len(triggers) == 2

    finally:

        conn.close()


# ============================================================
# 6. RUN AUDIT MODULE
# ============================================================

if __name__ == "__main__":

    print("\n===== AQUAPURE AUDIT MANAGEMENT SYSTEM =====")

    create_audit_protection()

    check_audit_protection()

    view_audit_logs()

    export_audit_logs()

    print("\nAUDIT MODULE COMPLETED SUCCESSFULLY.")
