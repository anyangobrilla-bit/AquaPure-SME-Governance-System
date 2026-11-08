
import sqlite3
from pathlib import Path
from datetime import datetime

backup = Path("backups/sme_governance_backup_20261108_200949_760937.db")

test_database = Path(
    "backups/recovery_test_" +
    datetime.now().strftime("%Y%m%d_%H%M%S") +
    ".db"
)

print("\n===== AQUAPURE RECOVERY TEST =====")

if not backup.exists():
    print("ERROR: Backup file not found.")

else:
    source = None
    destination = None

    try:
        source = sqlite3.connect(str(backup))
        destination = sqlite3.connect(str(test_database))

        source.backup(destination)

        destination.commit()

        cursor = destination.cursor()

        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM audit_logs
        """)
        audit_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM users
        """)
        user_count = cursor.fetchone()[0]

        print("Recovery test database:", test_database)
        print("Database integrity:", integrity)
        print("Audit records recovered:", audit_count)
        print("User records recovered:", user_count)

        if integrity == "ok" and audit_count == 93 and user_count == 3:
            print("\nPASS: BACKUP RECOVERY TEST SUCCESSFUL.")
        else:
            print("\nWARNING: Recovery verification needs review.")

    except Exception as error:
        print("Recovery test failed:", error)

    finally:
        if destination:
            destination.close()

        if source:
            source.close()
