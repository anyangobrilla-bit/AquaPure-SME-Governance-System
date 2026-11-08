
import sqlite3
from pathlib import Path

backup_path = Path("backups/sme_governance_backup_20261108_200949_760937.db")

print("\n========================================")
print(" AQUAPURE BACKUP CONTENT VERIFICATION")
print("========================================")

if not backup_path.exists():
    print("ERROR: Backup file not found.")
else:
    conn = sqlite3.connect(str(backup_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]

        cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        )

        count = cursor.fetchone()[0]

        print(f"{table_name}: {count} records")

    cursor.execute("PRAGMA integrity_check")
    print("\nDatabase integrity:", cursor.fetchone()[0])

    conn.close()

print("\nVERIFICATION COMPLETED.")
