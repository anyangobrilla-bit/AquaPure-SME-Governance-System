
# ============================================================
# AQUAPURE WATER SOLUTIONS
# SME GOVERNANCE AND CYBERSECURITY SYSTEM
# MAIN APPLICATION
# ============================================================

from getpass import getpass
from pathlib import Path

from security import login_user, check_permission

from risk_assessment import view_risks

from incident_response import (
    create_incident_action_table,
    view_incidents,
    report_incident,
    record_incident_action,
    update_incident_status
)

from incident_closure import (
    create_closure_tables,
    record_evidence,
    view_incident_evidence,
    close_incident,
    view_closure_records
)

from compliance import (
    view_compliance_checks,
    compliance_summary
)

from audit import view_audit_logs, log_action

from governance import view_governance_records

from data_purpose import view_data_purpose_register

from governance_monitor import run_governance_monitor

from backup import (
    backup_database,
    list_backups,
    restore_database
)


# ============================================================
# 1. DISPLAY MAIN DASHBOARD
# ============================================================

def display_menu():

    print("\n============================================")
    print(" AQUAPURE SME GOVERNANCE SYSTEM")
    print("============================================")

    print("1. View Risk Register")
    print("2. Incident Management")
    print("3. View Compliance Register")
    print("4. View Compliance Summary")
    print("5. View Audit Logs")
    print("6. View Data Governance Register")
    print("7. View Data Purpose Register")
    print("8. Automated Governance Monitoring")
    print("9. Logout")
    print("10. Database Backup and Recovery")

    print("============================================")


# ============================================================
# 2. DATABASE BACKUP AND RECOVERY SUBMENU
# ============================================================

def backup_management_menu(username, role):

    # Only Administrators can manage database backups.

    if role != "Administrator":

        print("\nACCESS DENIED.")
        print("Only Administrators can manage database backups.")

        log_action(
            username,
            "Denied access to database backup management"
        )

        return

    while True:

        print("\n============================================")
        print(" AQUAPURE DATABASE BACKUP AND RECOVERY")
        print("============================================")

        print("1. Create Database Backup")
        print("2. View Available Backups")
        print("3. Restore Database from Backup")
        print("4. Return to Main Dashboard")

        print("============================================")

        choice = input("Select an option (1-4): ").strip()

        # ----------------------------------------
        # OPTION 1: CREATE BACKUP
        # ----------------------------------------

        if choice == "1":

            print("\n--- CREATE DATABASE BACKUP ---")

            success = backup_database()

            if success:

                log_action(
                    username,
                    "Created a database backup successfully"
                )

        # ----------------------------------------
        # OPTION 2: VIEW AVAILABLE BACKUPS
        # ----------------------------------------

        elif choice == "2":

            list_backups()

        # ----------------------------------------
        # OPTION 3: RESTORE DATABASE
        # ----------------------------------------

        elif choice == "3":

            print("\n--- DATABASE RESTORATION ---")

            backup_folder = (
                Path(__file__).resolve().parent / "backups"
            )

            available_backups = sorted(
                backup_folder.glob("sme_governance_backup_*.db"),
                reverse=True
            ) if backup_folder.exists() else []

            if not available_backups:

                print("No valid database backups were found.")

            else:

                print("\nAvailable database backups:")

                for number, backup_file in enumerate(
                    available_backups,
                    start=1
                ):

                    print(f"{number}. {backup_file.name}")

                try:

                    selection = int(
                        input(
                            "\nEnter the backup number to restore: "
                        ).strip()
                    )

                    if selection < 1 or selection > len(
                        available_backups
                    ):

                        print("Invalid backup selection.")

                    else:

                        selected_backup = available_backups[
                            selection - 1
                        ]

                        print("\nSelected backup:")
                        print(selected_backup.name)

                        print(
                            "\nWARNING: Restoring a backup replaces "
                            "the current database contents."
                        )

                        print(
                            "A safety backup of the current database "
                            "will be created first."
                        )

                        confirmation = input(
                            "\nType RESTORE to confirm: "
                        ).strip()

                        if confirmation == "RESTORE":

                            success = restore_database(
                                selected_backup.name
                            )

                            if success:

                                log_action(
                                    username,
                                    "Restored database from backup: "
                                    + selected_backup.name
                                )

                                print(
                                    "\nRecovery operation recorded "
                                    "in the audit log."
                                )

                        else:

                            print("Database restoration cancelled.")

                except ValueError:

                    print("Invalid selection. Enter a number.")

        # ----------------------------------------
        # OPTION 4: RETURN TO DASHBOARD
        # ----------------------------------------

        elif choice == "4":

            print("\nReturning to main dashboard...")
            break

        else:

            print("Invalid selection. Choose between 1 and 4.")


# ============================================================
# 3. INCIDENT MANAGEMENT SUBMENU
# ============================================================

def incident_management_menu(username, role):

    while True:

        print("\n============================================")
        print("       AQUAPURE INCIDENT MANAGEMENT")
        print("============================================")

        print("1. View Incident Register")
        print("2. Report New Security Incident")
        print("3. Record Investigation Action")
        print("4. Update Incident Status")
        print("5. Record Investigation Evidence")
        print("6. View Investigation Evidence")
        print("7. Formally Close an Incident")
        print("8. View Formal Closure Records")
        print("9. Return to Main Dashboard")

        print("============================================")

        choice = input("Select an option (1-9): ").strip()

        # OPTION 1: VIEW INCIDENTS

        if choice == "1":

            if check_permission(role, "view_incidents"):
                view_incidents()

        # OPTION 2: REPORT NEW INCIDENT

        elif choice == "2":

            if check_permission(role, "manage_incidents"):

                print("\n--- REPORT NEW SECURITY INCIDENT ---")

                incident_type = input("Incident type: ")
                description = input("Incident description: ")

                severity = input(
                    "Severity (Low/Medium/High/Critical): "
                )

                report_incident(
                    incident_type,
                    description,
                    severity,
                    username
                )

        # OPTION 3: RECORD INVESTIGATION ACTION

        elif choice == "3":

            if check_permission(role, "manage_incidents"):

                print("\n--- RECORD INVESTIGATION ACTION ---")

                try:

                    incident_id = int(
                        input("Enter incident ID: ").strip()
                    )

                    action_taken = input(
                        "Describe the response action: "
                    )

                    record_incident_action(
                        incident_id,
                        action_taken,
                        username
                    )

                except ValueError:

                    print("Invalid incident ID. Enter a number.")

        # OPTION 4: UPDATE INCIDENT STATUS

        elif choice == "4":

            if check_permission(role, "manage_incidents"):

                print("\n--- UPDATE INCIDENT STATUS ---")

                try:

                    incident_id = int(
                        input("Enter incident ID: ").strip()
                    )

                    print("\nAvailable statuses:")
                    print("1. OPEN")
                    print("2. INVESTIGATING")

                    status_choice = input(
                        "Select new status (1-2): "
                    ).strip()

                    statuses = {
                        "1": "OPEN",
                        "2": "INVESTIGATING"
                    }

                    if status_choice in statuses:

                        update_incident_status(
                            incident_id,
                            statuses[status_choice],
                            username
                        )

                    else:

                        print("Invalid status selection.")
                        print(
                            "Use formal incident closure "
                            "to resolve an incident."
                        )

                except ValueError:

                    print("Invalid incident ID. Enter a number.")

        # OPTION 5: RECORD INVESTIGATION EVIDENCE

        elif choice == "5":

            if check_permission(role, "manage_incidents"):

                print("\n--- RECORD INVESTIGATION EVIDENCE ---")

                try:

                    incident_id = int(
                        input("Enter incident ID: ").strip()
                    )

                    evidence_type = input(
                        "Evidence type (e.g. Security Log, Screenshot): "
                    )

                    evidence_reference = input(
                        "Evidence reference or file reference: "
                    )

                    description = input(
                        "Describe the evidence: "
                    )

                    record_evidence(
                        incident_id,
                        evidence_type,
                        evidence_reference,
                        description,
                        username
                    )

                except ValueError:

                    print("Invalid incident ID. Enter a number.")

        # OPTION 6: VIEW INVESTIGATION EVIDENCE

        elif choice == "6":

            if check_permission(role, "view_incidents"):

                print("\n--- VIEW INVESTIGATION EVIDENCE ---")

                incident_choice = input(
                    "Enter incident ID, or press Enter to view all: "
                ).strip()

                if incident_choice == "":

                    view_incident_evidence()

                else:

                    try:

                        incident_id = int(incident_choice)

                        view_incident_evidence(incident_id)

                    except ValueError:

                        print("Invalid incident ID. Enter a number.")

        # OPTION 7: FORMAL INCIDENT CLOSURE

        elif choice == "7":

            if check_permission(role, "manage_incidents"):

                print("\n--- FORMAL INCIDENT CLOSURE ---")

                try:

                    incident_id = int(
                        input("Enter incident ID to close: ").strip()
                    )

                    print("\nProvide the formal closure details.")

                    root_cause = input(
                        "Identified root cause: "
                    ).strip()

                    corrective_action = input(
                        "Corrective action taken: "
                    ).strip()

                    preventive_action = input(
                        "Preventive action to avoid recurrence: "
                    ).strip()

                    closure_summary = input(
                        "Final incident closure summary: "
                    ).strip()

                    print("\n--- AUTHENTICATED CLOSURE APPROVAL ---")

                    approver_username = input(
                        "Approving officer username: "
                    ).strip()

                    approver_password = getpass(
                        "Approving officer password: "
                    )

                    if approver_username.lower() == username.lower():

                        print(
                            "\nAPPROVAL DENIED: "
                            "The person closing the incident "
                            "cannot approve their own closure."
                        )

                    else:

                        approver_role = login_user(
                            approver_username,
                            approver_password
                        )

                        if approver_role not in [
                            "Administrator",
                            "Manager"
                        ]:

                            print(
                                "\nAPPROVAL DENIED: "
                                "Only an authenticated Administrator "
                                "or Manager can approve incident closure."
                            )

                        else:

                            print(
                                "\nApprover authenticated successfully."
                            )

                            print("Approver role:", approver_role)

                            confirmation = input(
                                "\nConfirm formal closure? (yes/no): "
                            ).strip().lower()

                            if confirmation == "yes":

                                close_incident(
                                    incident_id,
                                    root_cause,
                                    corrective_action,
                                    preventive_action,
                                    closure_summary,
                                    username,
                                    approver_username
                                )

                            else:

                                print("Incident closure cancelled.")

                except ValueError:

                    print("Invalid incident ID. Enter a number.")

        # OPTION 8: VIEW FORMAL CLOSURE RECORDS

        elif choice == "8":

            if check_permission(role, "view_incidents"):
                view_closure_records()

        # OPTION 9: RETURN TO MAIN DASHBOARD

        elif choice == "9":

            print("\nReturning to main dashboard...")
            break

        else:

            print("Invalid selection. Choose between 1 and 9.")


# ============================================================
# 4. MAIN DASHBOARD OPERATIONS
# ============================================================

def run_dashboard(username, role):

    while True:

        display_menu()

        choice = input("Select an option (1-10): ").strip()

        # OPTION 1: RISK REGISTER

        if choice == "1":

            if check_permission(role, "view_risks"):
                view_risks()

        # OPTION 2: INCIDENT MANAGEMENT

        elif choice == "2":

            if check_permission(role, "view_incidents"):
                incident_management_menu(username, role)

        # OPTION 3: COMPLIANCE REGISTER

        elif choice == "3":

            if check_permission(role, "view_compliance"):
                view_compliance_checks()

        # OPTION 4: COMPLIANCE SUMMARY

        elif choice == "4":

            if check_permission(role, "view_compliance"):
                compliance_summary()

        # OPTION 5: AUDIT LOGS

        elif choice == "5":

            if check_permission(role, "view_audit"):
                view_audit_logs()

        # OPTION 6: DATA GOVERNANCE REGISTER

        elif choice == "6":

            if check_permission(role, "view_governance"):
                view_governance_records(role)

        # OPTION 7: DATA PURPOSE REGISTER

        elif choice == "7":

            if check_permission(role, "view_compliance"):
                view_data_purpose_register()

        # OPTION 8: AUTOMATED GOVERNANCE MONITOR

        elif choice == "8":

            if check_permission(role, "view_governance_monitor"):
                run_governance_monitor()

        # OPTION 9: LOGOUT

        elif choice == "9":

            print(f"\n{username} has logged out.")
            break

        # OPTION 10: DATABASE BACKUP AND RECOVERY

        elif choice == "10":

            backup_management_menu(username, role)

        else:

            print("Invalid selection. Choose between 1 and 10.")


# ============================================================
# 5. APPLICATION LOGIN
# ============================================================

def main():

    print("\n============================================")
    print(" WELCOME TO AQUAPURE GOVERNANCE SYSTEM")
    print("============================================")

    username = input("Enter username: ").strip()

    password = getpass("Enter password: ")

    role = login_user(username, password)

    if role:

        print("\nLogin successful.")
        print("Welcome:", username)
        print("Role:", role)

        create_incident_action_table()

        create_closure_tables()

        run_dashboard(username, role)

    else:

        print("\nAccess denied. Please check your login details.")


# ============================================================
# 6. APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
