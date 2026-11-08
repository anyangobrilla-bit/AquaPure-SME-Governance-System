
from database import connect_db

conn = connect_db()
cursor = conn.cursor()

print("\n======================================")
print("AQUAPURE DATABASE STRUCTURE")
print("======================================")

# Get all database tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tables = cursor.fetchall()

for table in tables:
    table_name = table[0]

    print("\nTABLE:", table_name)

    # Get the columns in each table
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    print("COLUMNS:")

    for column in columns:
        print("-", column[1])

conn.close()

print("\n======================================")
print("DATABASE INSPECTION COMPLETED")
print("======================================")
