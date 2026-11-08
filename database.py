
# ============================================================
# AQUAPURE WATER SOLUTIONS
# DATABASE MANAGEMENT MODULE
# ============================================================

import sqlite3
import os

# ------------------------------------------------------------
# 1. DATABASE CONFIGURATION
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "sme_governance.db"
)


# ------------------------------------------------------------
# 2. DATABASE CONNECTION
# ------------------------------------------------------------

def connect_db():
    """
    Connect to the AquaPure SQLite database.

    The absolute path ensures all project modules
    use the same database file.
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    return conn


# ------------------------------------------------------------
# 3. CREATE CORE DATABASE TABLES
# ------------------------------------------------------------

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    try:

        # User Management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # Customer Records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                classification TEXT DEFAULT 'CONFIDENTIAL'
            )
        """)

        # Risk Register
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_name TEXT NOT NULL,
                likelihood INTEGER,
                impact INTEGER,
                risk_score INTEGER,
                mitigation TEXT
            )
        """)

        # Incident Register
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                description TEXT,
                severity TEXT,
                status TEXT DEFAULT 'OPEN'
            )
        """)

        # Audit Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        print("\n============================================")
        print(" AQUAPURE DATABASE INITIALIZATION")
        print("============================================")
        print("Database created or verified successfully.")
        print("Database location:", DATABASE)
        print("Core database tables verified.")
        print("============================================")

    except sqlite3.Error as error:

        conn.rollback()

        print("Database initialization error:", error)

    finally:

        conn.close()


# ------------------------------------------------------------
# 4. DATABASE CONNECTION TEST
# ------------------------------------------------------------

def test_database_connection():

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT COUNT(*)
            FROM audit_logs
        """)

        total_logs = cursor.fetchone()[0]

        cursor.execute("""
            SELECT id, username, action, timestamp
            FROM audit_logs
            ORDER BY id DESC
            LIMIT 5
        """)

        latest_logs = cursor.fetchall()

        print("\n========== DATABASE CONNECTION TEST ==========")
        print("Database location:", DATABASE)
        print("Total audit records:", total_logs)

        print("\nLatest five audit records:")

        for log in latest_logs:

            print(
                log["id"],
                log["username"],
                log["action"],
                log["timestamp"]
            )

        print("==============================================")

    except sqlite3.Error as error:

        print("Database test failed:", error)

    finally:

        conn.close()


# ------------------------------------------------------------
# 5. RUN DATABASE MODULE
# ------------------------------------------------------------

if __name__ == "__main__":

    create_tables()

    test_database_connection()
