
# ============================================================
# AQUAPURE WATER SOLUTIONS
# RISK ASSESSMENT MODULE
# WITH AUTOMATIC AUDIT LOGGING
# ============================================================

from database import connect_db
from audit import log_action


# 1. Calculate the risk score
def calculate_risk_score(likelihood, impact):
    return likelihood * impact


# 2. Determine the risk level
def determine_risk_level(score):
    if score <= 5:
        return "Low"
    elif score <= 10:
        return "Medium"
    elif score <= 15:
        return "High"
    else:
        return "Critical"


# 3. Add or update a risk in the database
def add_risk(risk_name, likelihood, impact, mitigation):

    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        print("Likelihood and impact must be between 1 and 5.")
        return

    score = calculate_risk_score(likelihood, impact)
    level = determine_risk_level(score)

    conn = connect_db()
    cursor = conn.cursor()

    # Check whether this risk already exists
    cursor.execute(
        "SELECT id FROM risks WHERE risk_name = ?",
        (risk_name,)
    )

    existing_risk = cursor.fetchone()

    if existing_risk:
        cursor.execute("""
            UPDATE risks
            SET likelihood = ?,
                impact = ?,
                risk_score = ?,
                mitigation = ?
            WHERE id = ?
        """, (likelihood, impact, score, mitigation, existing_risk[0]))

        action = (
            f"Updated risk: {risk_name}. "
            f"Risk score: {score}. Risk level: {level}."
        )

        print("Existing risk updated successfully.")

    else:
        cursor.execute("""
            INSERT INTO risks
            (risk_name, likelihood, impact, risk_score, mitigation)
            VALUES (?, ?, ?, ?, ?)
        """, (risk_name, likelihood, impact, score, mitigation))

        action = (
            f"Added new risk: {risk_name}. "
            f"Risk score: {score}. Risk level: {level}."
        )

        print("New risk recorded successfully.")

    conn.commit()
    conn.close()

    # Automatically record the activity in the audit log
    log_action("admin", action)

    print("Risk score:", score)
    print("Risk level:", level)


# 4. Display all recorded risks
def view_risks():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, risk_name, likelihood, impact,
               risk_score, mitigation
        FROM risks
        ORDER BY risk_score DESC
    """)

    risks = cursor.fetchall()
    conn.close()

    print("\n========== AQUAPURE RISK REGISTER ==========")

    if not risks:
        print("No risks have been recorded.")
        return

    for risk in risks:
        risk_id, name, likelihood, impact, score, mitigation = risk

        level = determine_risk_level(score)

        print("\nRisk ID:", risk_id)
        print("Risk:", name)
        print("Likelihood:", likelihood)
        print("Impact:", impact)
        print("Risk Score:", score)
        print("Risk Level:", level)
        print("Mitigation:", mitigation)
        print("--------------------------------------------")


# 5. Run sample risk assessments
if __name__ == "__main__":

    print("\n===== AQUAPURE RISK ASSESSMENT SYSTEM =====")

    add_risk(
        "Unauthorized access to customer records",
        4,
        5,
        "Implement strong passwords, role-based access "
        "and multi-factor authentication."
    )

    add_risk(
        "Loss of customer data",
        3,
        5,
        "Perform regular backups and test data recovery."
    )

    add_risk(
        "Exposure of paper customer records",
        3,
        4,
        "Store paper files in locked cabinets and restrict access."
    )

    add_risk(
        "Employee misuse of confidential information",
        3,
        4,
        "Provide staff training and enforce confidentiality policies."
    )

    add_risk(
        "Malware or ransomware attack",
        4,
        5,
        "Install updated antivirus software and maintain secure backups."
    )

    view_risks()
