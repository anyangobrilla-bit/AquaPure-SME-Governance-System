
from database import connect_db


def run_governance_monitor():

    conn = connect_db()
    cursor = conn.cursor()

    alerts = []
    recommendations = []

    print("\n" + "=" * 55)
    print("       AQUAPURE AUTOMATED GOVERNANCE MONITOR")
    print("=" * 55)

    try:

        # 1. BUSINESS RISK MONITORING
        cursor.execute("""
            SELECT risk_name, risk_score, mitigation
            FROM risks
            ORDER BY risk_score DESC
        """)

        risks = cursor.fetchall()

        critical_risks = 0
        high_risks = 0

        print("\n1. BUSINESS RISK MONITORING")

        for risk in risks:

            name = risk["risk_name"]
            score = risk["risk_score"]
            mitigation = risk["mitigation"]

            if score >= 16:
                critical_risks += 1
                alerts.append(
                    f"CRITICAL RISK: {name} (Score: {score})"
                )

            elif score >= 10:
                high_risks += 1
                alerts.append(
                    f"HIGH RISK: {name} (Score: {score})"
                )

        print("Total risks:", len(risks))
        print("Critical risks:", critical_risks)
        print("High risks:", high_risks)

        if critical_risks:
            recommendations.append(
                "Prioritize critical risks and review their mitigation measures."
            )

        if high_risks:
            recommendations.append(
                "Monitor high risks and verify that mitigation actions are effective."
            )

        # 2. SECURITY INCIDENT MONITORING
        cursor.execute("""
            SELECT id, incident_type, severity, status
            FROM incidents
            ORDER BY id DESC
        """)

        incidents = cursor.fetchall()

        unresolved = 0

        print("\n2. SECURITY INCIDENT MONITORING")

        for incident in incidents:

            status = (incident["status"] or "").strip().upper()

            if status in ("OPEN", "INVESTIGATING"):
                unresolved += 1

                alerts.append(
                    f"UNRESOLVED INCIDENT: ID {incident['id']} - "
                    f"{incident['incident_type']} ({status})"
                )

        print("Total incidents:", len(incidents))
        print("Unresolved incidents:", unresolved)

        if unresolved:
            recommendations.append(
                "Investigate unresolved incidents, document response actions "
                "and update their status when resolved."
            )

        # 3. COMPLIANCE MONITORING
        cursor.execute("""
            SELECT control_code, framework, status, action_required
            FROM compliance_checks
            ORDER BY id
        """)

        compliance = cursor.fetchall()

        not_started = 0
        in_progress = 0
        needs_review = 0

        print("\n3. REGULATORY COMPLIANCE MONITORING")

        for item in compliance:

            status = (item["status"] or "").strip().lower()

            if status == "not started":
                not_started += 1
                alerts.append(
                    f"COMPLIANCE GAP: {item['control_code']} "
                    f"({item['framework']}) has not started."
                )

            elif status == "in progress":
                in_progress += 1

            elif status == "needs review":
                needs_review += 1
                alerts.append(
                    f"COMPLIANCE REVIEW REQUIRED: {item['control_code']}"
                )

        total_compliance = len(compliance)

        completed = sum(
            1 for item in compliance
            if (item["status"] or "").strip().lower() == "implemented"
        )

        progress = (
            completed / total_compliance * 100
            if total_compliance else 0
        )

        print("Total requirements:", total_compliance)
        print("Implemented:", completed)
        print("In progress:", in_progress)
        print("Not started:", not_started)
        print("Needs review:", needs_review)
        print("Fully implemented:", round(progress, 2), "%")

        if not_started or needs_review:
            recommendations.append(
                "Prioritize outstanding compliance requirements and "
                "record supporting evidence."
            )

        # 4. DATA PURPOSE AND PRIVACY MONITORING
        cursor.execute("""
            SELECT id, data_category, approval_status
            FROM data_purpose_register
            ORDER BY id
        """)

        purposes = cursor.fetchall()

        pending_approvals = 0

        print("\n4. DATA PURPOSE AND PRIVACY MONITORING")

        for purpose in purposes:

            status = (
                purpose["approval_status"] or ""
            ).strip().lower()

            if status not in ("approved", "authorised", "authorized"):
                pending_approvals += 1

                alerts.append(
                    f"DATA PURPOSE APPROVAL GAP: "
                    f"{purpose['data_category']} - "
                    f"Status: {purpose['approval_status']}"
                )

        print("Data purpose records:", len(purposes))
        print("Records requiring approval review:", pending_approvals)

        if pending_approvals:
            recommendations.append(
                "Review data processing purposes and obtain the required "
                "approval before relying on the recorded processing purpose."
            )

        # 5. SECURITY ACTIVITY MONITORING
        cursor.execute("""
            SELECT action, COUNT(*) AS total
            FROM audit_logs
            WHERE LOWER(action) LIKE '%failed login%'
               OR LOWER(action) LIKE '%denied%'
            GROUP BY action
        """)

        security_events = cursor.fetchall()

        failed_logins = 0
        denied_events = 0

        print("\n5. SECURITY ACTIVITY MONITORING")

        for event in security_events:

            action = event["action"]
            count = event["total"]

            print(action, ":", count)

            if "failed login" in action.lower():
                failed_logins += count

            if "denied" in action.lower():
                denied_events += count

        print("Total failed login events:", failed_logins)
        print("Total denied access events:", denied_events)

        if failed_logins:
            alerts.append(
                f"SECURITY WARNING: {failed_logins} failed login events recorded."
            )

            recommendations.append(
                "Review failed login events and investigate suspicious "
                "authentication activity."
            )

        if denied_events:
            alerts.append(
                f"ACCESS CONTROL WARNING: {denied_events} denied access events recorded."
            )

            recommendations.append(
                "Review denied access events to confirm that role-based "
                "permissions are working correctly."
            )

        # 6. FINAL GOVERNANCE ALERTS
        print("\n" + "=" * 55)
        print("6. GOVERNANCE ALERTS")
        print("=" * 55)

        if alerts:
            for number, alert in enumerate(alerts, start=1):
                print(f"{number}. {alert}")
        else:
            print("No governance alerts detected.")

        # 7. GOVERNANCE RECOMMENDATIONS
        print("\n" + "=" * 55)
        print("7. RECOMMENDED ACTIONS")
        print("=" * 55)

        if recommendations:
            for number, recommendation in enumerate(
                recommendations, start=1
            ):
                print(f"{number}. {recommendation}")
        else:
            print("No additional actions identified.")

        print("\n" + "=" * 55)
        print("GOVERNANCE MONITORING COMPLETED")
        print("=" * 55)

    finally:
        conn.close()


if __name__ == "__main__":
    run_governance_monitor()
