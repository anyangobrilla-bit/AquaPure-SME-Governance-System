
from database import connect_db
from audit import log_action
from security import check_classification_access


# ============================================================
# 1. CREATE DATA GOVERNANCE TABLE
# ============================================================

def create_governance_table():

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS governance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_category TEXT NOT NULL UNIQUE,
                data_description TEXT NOT NULL,
                classification TEXT NOT NULL,
                data_owner TEXT NOT NULL,
                responsible_person TEXT NOT NULL,
                protection_policy TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("Governance table created successfully.")

    finally:
        conn.close()


# ============================================================
# 2. ADD GOVERNANCE RECORD
# ============================================================

def add_governance_record(
    data_category,
    data_description,
    classification,
    data_owner,
    responsible_person,
    protection_policy
):

    allowed_classifications = [
        "PUBLIC",
        "INTERNAL",
        "CONFIDENTIAL",
        "RESTRICTED"
    ]

    classification = classification.strip().upper()

    if classification not in allowed_classifications:
        print("Invalid data classification.")
        return

    fields = [
        data_category,
        data_description,
        data_owner,
        responsible_person,
        protection_policy
    ]

    if any(not value or not value.strip() for value in fields):
        print("All fields are required.")
        return

    conn = connect_db()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM governance_records
            WHERE LOWER(data_category) = LOWER(?)
        """, (data_category.strip(),))

        if cursor.fetchone():
            print("This data category already exists.")
            return

        cursor.execute("""
            INSERT INTO governance_records (
                data_category,
                data_description,
                classification,
                data_owner,
                responsible_person,
                protection_policy
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data_category.strip(),
            data_description.strip(),
            classification,
            data_owner.strip(),
            responsible_person.strip(),
            protection_policy.strip()
        ))

        conn.commit()

        record_id = cursor.lastrowid

    finally:
        conn.close()

    log_action(
        "admin",
        f"Added governance record ID {record_id}: {data_category}"
    )

    print("Governance record added successfully.")
    print("Record ID:", record_id)


# ============================================================
# 3. VIEW GOVERNANCE RECORDS WITH ACCESS CONTROL
# ============================================================

def view_governance_records(role):

    if not role:
        print("ACCESS DENIED: Login is required.")
        return

    conn = connect_db()

    try:
        cursor = conn.cursor()

        # Retrieve only record metadata first.
        # Sensitive descriptions are fetched only after access
        # has been granted.

        cursor.execute("""
            SELECT id, data_category, classification
            FROM governance_records
            ORDER BY id
        """)

        record_metadata = cursor.fetchall()

        print("\n========== AQUAPURE DATA GOVERNANCE REGISTER ==========")
        print("Logged-in Role:", role)

        if not record_metadata:
            print("No governance records found.")
            return

        accessible_ids = []

        for record in record_metadata:

            record_id = record[0]
            category = record[1]
            classification = record[2]

            if check_classification_access(role, classification):
                accessible_ids.append(record_id)

        if not accessible_ids:
            print("\nNo records are available for your access level.")
            return

        print("\nAccessible Records:", len(accessible_ids))

        for record_id in accessible_ids:

            cursor.execute("""
                SELECT id, data_category, data_description,
                       classification, data_owner,
                       responsible_person, protection_policy,
                       created_at
                FROM governance_records
                WHERE id = ?
            """, (record_id,))

            record = cursor.fetchone()

            if record:

                print("\nRecord ID:", record[0])
                print("Data Category:", record[1])
                print("Description:", record[2])
                print("Classification:", record[3])
                print("Data Owner:", record[4])
                print("Responsible Person:", record[5])
                print("Protection Policy:", record[6])
                print("Created At:", record[7])
                print("----------------------------------------")

    finally:
        conn.close()


# ============================================================
# 4. REGISTER INITIAL AQUAPURE DATA CATEGORIES
# ============================================================

def register_initial_governance_records():

    records = [

        (
            "Customer Records",
            "Customer names, telephone numbers and contact information.",
            "CONFIDENTIAL",
            "Customer Relations Manager",
            "Data Steward",
            "Restrict access to authorized staff and protect customer information."
        ),

        (
            "Employee Records",
            "Employee personal details, employment records and contacts.",
            "CONFIDENTIAL",
            "Human Resources Manager",
            "HR Officer",
            "Store employee records securely and restrict unauthorized access."
        ),

        (
            "Financial Records",
            "Business transactions, payments, revenue and financial statements.",
            "RESTRICTED",
            "Finance Manager",
            "Accountant",
            "Limit access to authorized finance personnel and maintain secure backups."
        ),

        (
            "Business Information",
            "Internal business plans, operational procedures and management reports.",
            "INTERNAL",
            "Business Manager",
            "Operations Manager",
            "Allow access to authorized employees and prevent unauthorized disclosure."
        )

    ]

    print("\nREGISTERING AQUAPURE DATA CATEGORIES")

    for record in records:
        add_governance_record(*record)


# ============================================================
# 5. RUN GOVERNANCE MODULE
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("AQUAPURE DATA GOVERNANCE MODULE")
    print("======================================")

    create_governance_table()

    register_initial_governance_records()

    print("\nData governance module completed successfully.")
    print("Use the authenticated dashboard to view records.")
