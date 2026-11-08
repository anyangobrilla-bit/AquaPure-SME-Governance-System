
from database import connect_db
from audit import log_action
import pandas as pd


def create_data_purpose_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_purpose_register (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_category TEXT UNIQUE NOT NULL,
            information_collected TEXT NOT NULL,
            purpose_of_collection TEXT NOT NULL,
            how_information_is_used TEXT NOT NULL,
            authorized_users TEXT NOT NULL,
            evidence_required TEXT NOT NULL,
            approval_status TEXT DEFAULT 'Pending Approval',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("Data purpose register table created successfully.")


def add_data_purpose(
    data_category,
    information_collected,
    purpose_of_collection,
    how_information_is_used,
    authorized_users,
    evidence_required
):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO data_purpose_register (
                data_category,
                information_collected,
                purpose_of_collection,
                how_information_is_used,
                authorized_users,
                evidence_required
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data_category,
            information_collected,
            purpose_of_collection,
            how_information_is_used,
            authorized_users,
            evidence_required
        ))

        conn.commit()
        print("Data purpose record added successfully.")

        log_action(
            "admin",
            f"Added data purpose record: {data_category}"
        )

    except Exception as error:
        print("Unable to add record:", error)

    finally:
        conn.close()


def view_data_purpose_register():
    create_data_purpose_table()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM data_purpose_register
        ORDER BY id
    """)

    records = cursor.fetchall()
    conn.close()

    print("\n========== AQUAPURE DATA PURPOSE REGISTER ==========")

    if not records:
        print("No data purpose records found.")
        return

    for record in records:
        print(f"""
Record ID: {record[0]}
Data Category: {record[1]}
Information Collected: {record[2]}
Purpose of Collection: {record[3]}
How Information Is Used: {record[4]}
Authorized Users: {record[5]}
Evidence Required: {record[6]}
Approval Status: {record[7]}
----------------------------------------
""")


def update_purpose_approval(data_category, new_status):
    allowed_statuses = [
        "Pending Approval",
        "Approved",
        "Needs Review"
    ]

    if new_status not in allowed_statuses:
        print("Invalid approval status.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE data_purpose_register
        SET approval_status = ?
        WHERE data_category = ?
    """, (new_status, data_category))

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated:
        print("Data purpose approval status updated successfully.")
        log_action(
            "admin",
            f"Updated purpose approval for {data_category} to {new_status}"
        )
    else:
        print("Data category not found.")


def export_data_purpose_report(
    filename="data_purpose_register.xlsx"
):
    conn = connect_db()

    dataframe = pd.read_sql_query(
        "SELECT * FROM data_purpose_register",
        conn
    )

    conn.close()

    dataframe.to_excel(filename, index=False)

    print("\nData purpose report exported successfully.")
    print("File:", filename)

    log_action("admin", "Exported data purpose register")


def initialize_data_purpose_register():
    create_data_purpose_table()

    sample_records = [
        (
            "Customer Records",
            "Customer names and telephone numbers.",
            "Customer registration, service delivery and customer communication.",
            "Identify customers, manage water refill requests and communicate service information.",
            "Customer Relations Manager; Data Steward",
            "Approved customer registration forms and documented customer data purpose and access register."
        ),
        (
            "Employee Records",
            "Employee names, contact details and employment information.",
            "Recruitment, employment administration and payroll management.",
            "Manage employee records, employment processes and salary administration.",
            "HR Manager; HR Officer",
            "Approved employee information forms and documented HR data handling procedures."
        ),
        (
            "Financial Records",
            "Payment details, transaction records and financial information.",
            "Billing, payment processing, accounting and financial reporting.",
            "Record customer payments, reconcile transactions and prepare financial reports.",
            "Finance Manager; Accountant",
            "Approved financial record procedures and documented access authorization."
        )
    ]

    conn = connect_db()
    cursor = conn.cursor()

    added = 0

    for record in sample_records:
        cursor.execute("""
            INSERT OR IGNORE INTO data_purpose_register (
                data_category,
                information_collected,
                purpose_of_collection,
                how_information_is_used,
                authorized_users,
                evidence_required
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, record)

        added += cursor.rowcount

    conn.commit()
    conn.close()

    if added:
        log_action(
            "admin",
            f"Initialized data purpose register with {added} records"
        )

    print("\nData purpose register initialization complete.")
    print("New records added:", added)


if __name__ == "__main__":
    initialize_data_purpose_register()
    view_data_purpose_register()
