
# ============================================================
# AQUAPURE WATER SOLUTIONS
# DATABASE BACKUP AND RECOVERY MODULE
# ============================================================

import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# 1. DATABASE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "sme_governance.db"

BACKUP_DIR = BASE_DIR / "backups"


# ============================================================
# 2. CREATE DATABASE BACKUP
# ============================================================

def backup_database():

    print("\n========================================")
    print(" AQUAPURE DATABASE BACKUP")
    print("========================================")

    if not DATABASE_PATH.exists():
        print("ERROR: Main database was not found.")
        return False

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    backup_path = BACKUP_DIR / f"sme_governance_backup_{timestamp}.db"

    source = None
    destination = None

    try:

        source = sqlite3.connect(str(DATABASE_PATH))
        destination = sqlite3.connect(str(backup_path))

        source.backup(destination)

        destination.commit()

        cursor = destination.cursor()

        cursor.execute("PRAGMA integrity_check")

        result = cursor.fetchone()[0]

        if result != "ok":
            raise sqlite3.DatabaseError(
                "Backup integrity verification failed."
            )

        print("Database backup created successfully.")
        print("Backup location:", backup_path)
        print("Integrity check: PASSED")

        return True

    except Exception as error:

        print("Backup failed:", error)

        if backup_path.exists():
            backup_path.unlink()

        return False

    finally:

        if destination:
            destination.close()

        if source:
            source.close()


# ============================================================
# 3. DISPLAY AVAILABLE BACKUPS
# ============================================================

def list_backups():

    print("\n========================================")
    print(" AQUAPURE AVAILABLE DATABASE BACKUPS")
    print("========================================")

    if not BACKUP_DIR.exists():

        print("No backup folder found.")
        return

    backups = sorted(
        BACKUP_DIR.glob("sme_governance_backup_*.db"),
        reverse=True
    )

    if not backups:

        print("No database backups available.")
        return

    for number, backup in enumerate(backups, start=1):

        size_kb = backup.stat().st_size / 1024

        print(f"\n{number}. {backup.name}")
        print(f"   Size: {size_kb:.2f} KB")


# ============================================================
# 4. RESTORE DATABASE FROM A BACKUP
# ============================================================

def restore_database(backup_filename):

    print("\n========================================")
    print(" AQUAPURE DATABASE RECOVERY")
    print("========================================")

    BACKUP_DIR.mkdir(exist_ok=True)

    backup_path = (BACKUP_DIR / Path(backup_filename).name).resolve()

    if backup_path.parent != BACKUP_DIR.resolve():
        print("ERROR: Invalid backup location.")
        return False

    if not backup_path.is_file():
        print("ERROR: Selected backup does not exist.")
        return False

    source = None
    destination = None

    try:

        # Verify backup before restoration.
        source = sqlite3.connect(str(backup_path))

        cursor = source.cursor()

        cursor.execute("PRAGMA integrity_check")

        if cursor.fetchone()[0] != "ok":
            print("ERROR: Backup database is damaged.")
            return False

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """)

        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {"users", "audit_logs"}

        if not required_tables.issubset(tables):
            print("ERROR: Backup does not contain required tables.")
            return False

        source.close()
        source = None

        # Preserve the current database before restoring.
        print("Creating safety backup of current database...")

        if not backup_database():
            print("Recovery cancelled. Safety backup failed.")
            return False

        # Restore the selected backup.
        source = sqlite3.connect(str(backup_path))
        destination = sqlite3.connect(str(DATABASE_PATH))

        source.backup(destination)

        destination.commit()

        print("\nDATABASE RESTORED SUCCESSFULLY.")
        print("Restored from:", backup_path.name)
        print("Current database safety backup preserved.")

        return True

    except Exception as error:

        print("Database recovery failed:", error)
        return False

    finally:

        if destination:
            destination.close()

        if source:
            source.close()


# ============================================================
# 5. RUN BACKUP MODULE
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print(" AQUAPURE BACKUP MANAGEMENT SYSTEM")
    print("========================================")

    backup_database()

    list_backups()

    print("\nBACKUP MANAGEMENT MODULE COMPLETED.")
