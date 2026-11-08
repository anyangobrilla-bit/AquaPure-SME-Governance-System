
# ============================================================
# AQUAPURE WATER SOLUTIONS
# DATABASE BACKUP, RECOVERY AND AUTOMATED RETENTION MODULE
# ============================================================

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# 1. DATABASE LOCATIONS AND RETENTION SETTINGS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "sme_governance.db"

BACKUP_DIR = BASE_DIR / "backups"

MAX_BACKUPS = 10


# ============================================================
# 2. VERIFY BACKUP INTEGRITY
# ============================================================

def verify_backup_file(backup_path):

    connection = None

    try:
        connection = sqlite3.connect(str(backup_path))
        cursor = connection.cursor()

        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()

        return result is not None and result[0] == "ok"

    except Exception as error:
        print(f"Backup verification failed: {error}")
        return False

    finally:
        if connection:
            connection.close()


# ============================================================
# 3. CREATE DATABASE BACKUP
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

    backup_path = (
        BACKUP_DIR /
        f"sme_governance_backup_{timestamp}.db"
    )

    source = None
    destination = None

    try:
        source = sqlite3.connect(str(DATABASE_PATH))
        destination = sqlite3.connect(str(backup_path))

        source.backup(destination)
        destination.commit()

        destination.close()
        destination = None

        source.close()
        source = None

        if not verify_backup_file(backup_path):
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
# 4. DISPLAY AVAILABLE BACKUPS
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

        if verify_backup_file(backup):
            print("   Integrity: PASSED")
        else:
            print("   Integrity: FAILED")


# ============================================================
# 5. AUTOMATIC BACKUP RETENTION
# ============================================================

def apply_backup_retention():

    print("\n========================================")
    print(" AQUAPURE BACKUP RETENTION MANAGEMENT")
    print("========================================")

    if not BACKUP_DIR.exists():
        print("No backup folder found.")
        return False

    backups = sorted(
        BACKUP_DIR.glob("sme_governance_backup_*.db"),
        key=lambda item: item.stat().st_mtime,
        reverse=True
    )

    if len(backups) <= MAX_BACKUPS:
        print(f"Current backups: {len(backups)}")
        print(f"Retention limit: {MAX_BACKUPS}")
        print("No old backups need to be removed.")
        return True

    retained_backups = backups[:MAX_BACKUPS]
    older_backups = backups[MAX_BACKUPS:]

    print(f"Backups to retain: {len(retained_backups)}")
    print(f"Older backups identified: {len(older_backups)}")

    # Verify every backup that will be retained.
    print("\nVerifying retained backups...")

    for backup in retained_backups:

        if not verify_backup_file(backup):
            print("ERROR: A retained backup failed verification.")
            print("No older backups have been deleted.")
            return False

    print("All retained backups passed integrity checks.")

    # Delete older backups only after verification succeeds.
    deleted_count = 0

    for backup in older_backups:

        try:
            backup.unlink()
            deleted_count += 1

        except OSError as error:
            print(f"Could not remove {backup.name}: {error}")

    print(f"\nOlder backups removed: {deleted_count}")
    print(f"Backups retained: {len(retained_backups)}")

    return True


# ============================================================
# 6. RUN AUTOMATED SCHEDULED BACKUP
# ============================================================

def run_scheduled_backup():

    print("\n========================================")
    print(" AQUAPURE AUTOMATED DAILY BACKUP")
    print("========================================")

    print("Starting scheduled database backup...")

    if not backup_database():
        print("AUTOMATED BACKUP FAILED.")
        return False

    print("\nApplying backup retention policy...")

    retention_success = apply_backup_retention()

    # Record the automated backup in the audit log.
    try:
        from audit import log_action

        log_action(
            "SYSTEM",
            "Automated scheduled database backup completed successfully"
        )

    except Exception as error:
        print("WARNING: Audit logging failed:", error)

    if retention_success:
        print("\nAUTOMATED BACKUP COMPLETED SUCCESSFULLY.")
    else:
        print("\nBACKUP SUCCEEDED, BUT RETENTION NEEDS ATTENTION.")

    return True


# ============================================================
# 7. RESTORE DATABASE FROM A BACKUP
# ============================================================

def restore_database(backup_filename):

    print("\n========================================")
    print(" AQUAPURE DATABASE RECOVERY")
    print("========================================")

    BACKUP_DIR.mkdir(exist_ok=True)

    backup_path = (
        BACKUP_DIR / Path(backup_filename).name
    ).resolve()

    if backup_path.parent != BACKUP_DIR.resolve():
        print("ERROR: Invalid backup location.")
        return False

    if not backup_path.is_file():
        print("ERROR: Selected backup does not exist.")
        return False

    source = None
    destination = None

    try:

        if not verify_backup_file(backup_path):
            print("ERROR: Backup database is damaged.")
            return False

        source = sqlite3.connect(str(backup_path))
        cursor = source.cursor()

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

        # Preserve the current database before restoration.
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
# 8. RUN BACKUP MODULE
# ============================================================

if __name__ == "__main__":

    if "--scheduled" in sys.argv:

        run_scheduled_backup()

    else:

        print("\n========================================")
        print(" AQUAPURE BACKUP MANAGEMENT SYSTEM")
        print("========================================")

        backup_database()

        list_backups()

        print("\nBACKUP MANAGEMENT MODULE COMPLETED.")
