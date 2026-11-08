
# ============================================================
# AQUAPURE WATER SOLUTIONS
# CONSOLIDATED GOVERNANCE AND CYBERSECURITY REPORT
# ============================================================

import pandas as pd

from database import connect_db

from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter


def generate_consolidated_report():

    conn = connect_db()

    try:

        # ====================================================
        # 1. RISK REGISTER
        # ====================================================

        risks = pd.read_sql_query("""
            SELECT
                id AS Risk_ID,
                risk_name AS Risk,
                likelihood AS Likelihood,
                impact AS Impact,
                risk_score AS Risk_Score,
                mitigation AS Mitigation
            FROM risks
            ORDER BY risk_score DESC
        """, conn)


        # ====================================================
        # 2. INCIDENT REGISTER
        # ====================================================

        incidents = pd.read_sql_query("""
            SELECT
                i.id AS Incident_ID,
                i.incident_type AS Incident_Type,
                i.description AS Description,
                i.severity AS Severity,
                i.status AS Status,
                GROUP_CONCAT(a.action_taken, ' | ') AS Response_Actions,
                GROUP_CONCAT(a.recorded_by, ' | ') AS Recorded_By,
                GROUP_CONCAT(a.action_date, ' | ') AS Action_Dates
            FROM incidents i
            LEFT JOIN incident_actions a
                ON i.id = a.incident_id
            GROUP BY i.id
            ORDER BY i.id DESC
        """, conn)


        # ====================================================
        # 3. COMPLIANCE REGISTER
        # ====================================================

        compliance = pd.read_sql_query("""
            SELECT
                id AS Record_ID,
                framework AS Framework,
                control_code AS Control_Code,
                requirement AS Requirement,
                status AS Status,
                evidence AS Evidence,
                action_required AS Action_Required,
                responsible_person AS Responsible_Person
            FROM compliance_checks
            ORDER BY id
        """, conn)


        # ====================================================
        # 4. COMPLIANCE SUMMARY
        # ====================================================

        total = len(compliance)

        if total:

            statuses = (
                compliance["Status"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            implemented = (statuses == "Implemented").sum()
            in_progress = (statuses == "In Progress").sum()
            not_started = (statuses == "Not Started").sum()
            needs_review = (statuses == "Needs Review").sum()

        else:

            implemented = 0
            in_progress = 0
            not_started = 0
            needs_review = 0

        # Weighted implementation progress:
        # Implemented = 100%
        # In Progress = 50%
        # Not Started = 0%
        # Needs Review = 0%

        progress = (
            ((implemented + (in_progress * 0.5)) / total) * 100
            if total else 0
        )

        summary = pd.DataFrame({

            "Metric": [
                "Total Requirements",
                "Implemented",
                "In Progress",
                "Not Started",
                "Needs Review",
                "Implementation Progress (%)"
            ],

            "Value": [
                total,
                implemented,
                in_progress,
                not_started,
                needs_review,
                round(progress, 2)
            ]

        })


        # ====================================================
        # 5. AUDIT LOGS
        # ====================================================

        audit_logs = pd.read_sql_query("""
            SELECT
                id AS Log_ID,
                username AS Username,
                action AS Action,
                timestamp AS Timestamp
            FROM audit_logs
            ORDER BY id DESC
        """, conn)


        # ====================================================
        # 6. DATA GOVERNANCE REGISTER
        # ====================================================

        governance = pd.read_sql_query("""
            SELECT
                id AS Record_ID,
                data_category AS Data_Category,
                data_description AS Description,
                classification AS Classification,
                data_owner AS Data_Owner,
                responsible_person AS Responsible_Person,
                protection_policy AS Protection_Policy,
                created_at AS Created_At
            FROM governance_records
            ORDER BY id
        """, conn)


        # ====================================================
        # 7. DATA PURPOSE REGISTER
        # ====================================================

        data_purpose = pd.read_sql_query("""
            SELECT
                id AS Record_ID,
                data_category AS Data_Category,
                information_collected AS Information_Collected,
                purpose_of_collection AS Purpose_Of_Collection,
                how_information_is_used AS How_Information_Is_Used,
                authorized_users AS Authorized_Users,
                evidence_required AS Evidence_Required,
                approval_status AS Approval_Status,
                created_at AS Created_At
            FROM data_purpose_register
            ORDER BY id
        """, conn)


        # ====================================================
        # 8. EXPORT REPORT AND CREATE DASHBOARD
        # ====================================================

        filename = "AquaPure_Governance_Report.xlsx"

        with pd.ExcelWriter(
            filename,
            engine="openpyxl"
        ) as writer:

            # Export seven existing worksheets

            risks.to_excel(
                writer,
                sheet_name="Risk Register",
                index=False
            )

            incidents.to_excel(
                writer,
                sheet_name="Incident Register",
                index=False
            )

            compliance.to_excel(
                writer,
                sheet_name="Compliance Register",
                index=False
            )

            summary.to_excel(
                writer,
                sheet_name="Compliance Summary",
                index=False
            )

            audit_logs.to_excel(
                writer,
                sheet_name="Audit Logs",
                index=False
            )

            governance.to_excel(
                writer,
                sheet_name="Data Governance",
                index=False
            )

            data_purpose.to_excel(
                writer,
                sheet_name="Data Purpose Register",
                index=False
            )


            # =================================================
            # GOVERNANCE DASHBOARD
            # =================================================

            dashboard = writer.book.create_sheet(
                "Governance Dashboard"
            )

            # Dashboard title

            dashboard.merge_cells("A1:H1")

            dashboard["A1"] = (
                "AQUAPURE GOVERNANCE DASHBOARD"
            )

            dashboard["A1"].font = Font(
                bold=True,
                size=18,
                color="FFFFFF"
            )

            dashboard["A1"].fill = PatternFill(
                fill_type="solid",
                fgColor="17365D"
            )

            dashboard["A1"].alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

            dashboard.row_dimensions[1].height = 35


            # Dashboard subtitle

            dashboard.merge_cells("A2:H2")

            dashboard["A2"] = (
                "SME Governance and Cybersecurity Overview"
            )

            dashboard["A2"].font = Font(
                italic=True,
                size=11,
                color="666666"
            )

            dashboard["A2"].alignment = Alignment(
                horizontal="center"
            )


            # =================================================
            # KEY PERFORMANCE INDICATORS (KPIs)
            # =================================================

            kpis = [

                ("Total Risks", len(risks)),
                ("Security Incidents", len(incidents)),
                ("Compliance Progress", f"{round(progress, 2)}%"),
                ("Audit Activities", len(audit_logs)),
                ("Data Governance Records", len(governance)),
                ("Data Purpose Records", len(data_purpose))

            ]

            positions = [

                ("A4", "B4"),
                ("C4", "D4"),
                ("E4", "F4"),
                ("G4", "H4"),
                ("A6", "B6"),
                ("C6", "D6")

            ]

            for (label, value), (label_cell, value_cell) in zip(
                kpis, positions
            ):

                dashboard[label_cell] = label
                dashboard[value_cell] = value

                dashboard[label_cell].font = Font(
                    bold=True,
                    color="FFFFFF"
                )

                dashboard[label_cell].fill = PatternFill(
                    fill_type="solid",
                    fgColor="4472C4"
                )

                dashboard[value_cell].font = Font(
                    bold=True,
                    size=14,
                    color="17365D"
                )

                dashboard[value_cell].alignment = Alignment(
                    horizontal="center",
                    vertical="center"
                )


            # =================================================
            # RISK DISTRIBUTION DATA
            # =================================================

            dashboard["A9"] = "RISK DISTRIBUTION"

            dashboard["A9"].font = Font(
                bold=True,
                size=12
            )

            dashboard["A10"] = "Risk Level"
            dashboard["B10"] = "Number of Risks"

            risk_levels = {

                "Critical": (
                    risks["Risk_Score"] >= 16
                ).sum(),

                "High": (
                    (risks["Risk_Score"] >= 10) &
                    (risks["Risk_Score"] < 16)
                ).sum(),

                "Medium": (
                    (risks["Risk_Score"] >= 5) &
                    (risks["Risk_Score"] < 10)
                ).sum(),

                "Low": (
                    risks["Risk_Score"] < 5
                ).sum()

            }

            for row, (level, count) in enumerate(
                risk_levels.items(),
                start=11
            ):

                dashboard.cell(
                    row=row,
                    column=1,
                    value=level
                )

                dashboard.cell(
                    row=row,
                    column=2,
                    value=int(count)
                )


            # =================================================
            # INCIDENT STATUS DATA
            # =================================================

            dashboard["D9"] = "INCIDENT STATUS"

            dashboard["D9"].font = Font(
                bold=True,
                size=12
            )

            dashboard["D10"] = "Incident Status"
            dashboard["E10"] = "Number of Incidents"

            incident_counts = (
                incidents["Status"]
                .fillna("Unspecified")
                .value_counts()
            )

            for row, (status, count) in enumerate(
                incident_counts.items(),
                start=11
            ):

                dashboard.cell(
                    row=row,
                    column=4,
                    value=status
                )

                dashboard.cell(
                    row=row,
                    column=5,
                    value=int(count)
                )


            # =================================================
            # COMPLIANCE STATUS DATA
            # =================================================

            dashboard["G9"] = "COMPLIANCE STATUS"

            dashboard["G9"].font = Font(
                bold=True,
                size=12
            )

            dashboard["G10"] = "Status"
            dashboard["H10"] = "Requirements"

            compliance_counts = {

                "Implemented": implemented,
                "In Progress": in_progress,
                "Not Started": not_started,
                "Needs Review": needs_review

            }

            for row, (status, count) in enumerate(
                compliance_counts.items(),
                start=11
            ):

                dashboard.cell(
                    row=row,
                    column=7,
                    value=status
                )

                dashboard.cell(
                    row=row,
                    column=8,
                    value=int(count)
                )


            # =================================================
            # FORMAT DASHBOARD HEADINGS
            # =================================================

            for row in [10]:

                for cell in dashboard[row]:

                    cell.font = Font(
                        bold=True,
                        color="FFFFFF"
                    )

                    cell.fill = PatternFill(
                        fill_type="solid",
                        fgColor="5B9BD5"
                    )


            # =================================================
            # CHART 1: RISK DISTRIBUTION
            # =================================================

            risk_chart = BarChart()

            risk_chart.type = "col"

            risk_chart.title = "Risk Distribution"

            risk_chart.y_axis.title = "Number of Risks"

            risk_chart.x_axis.title = "Risk Level"

            risk_data = Reference(
                dashboard,
                min_col=2,
                min_row=10,
                max_row=14
            )

            risk_categories = Reference(
                dashboard,
                min_col=1,
                min_row=11,
                max_row=14
            )

            risk_chart.add_data(
                risk_data,
                titles_from_data=True
            )

            risk_chart.set_categories(
                risk_categories
            )

            risk_chart.height = 7
            risk_chart.width = 12

            dashboard.add_chart(
                risk_chart,
                "A17"
            )


            # =================================================
            # CHART 2: INCIDENT STATUS
            # =================================================

            incident_chart = BarChart()

            incident_chart.type = "col"

            incident_chart.title = (
                "Security Incidents by Status"
            )

            incident_chart.y_axis.title = (
                "Number of Incidents"
            )

            incident_last_row = (
                10 + len(incident_counts)
            )

            incident_data = Reference(
                dashboard,
                min_col=5,
                min_row=10,
                max_row=incident_last_row
            )

            incident_categories = Reference(
                dashboard,
                min_col=4,
                min_row=11,
                max_row=incident_last_row
            )

            incident_chart.add_data(
                incident_data,
                titles_from_data=True
            )

            incident_chart.set_categories(
                incident_categories
            )

            incident_chart.height = 7
            incident_chart.width = 12

            dashboard.add_chart(
                incident_chart,
                "D17"
            )


            # =================================================
            # CHART 3: COMPLIANCE STATUS
            # =================================================

            compliance_chart = BarChart()

            compliance_chart.type = "col"

            compliance_chart.title = (
                "Compliance Implementation Status"
            )

            compliance_chart.y_axis.title = (
                "Number of Requirements"
            )

            compliance_data = Reference(
                dashboard,
                min_col=8,
                min_row=10,
                max_row=14
            )

            compliance_categories = Reference(
                dashboard,
                min_col=7,
                min_row=11,
                max_row=14
            )

            compliance_chart.add_data(
                compliance_data,
                titles_from_data=True
            )

            compliance_chart.set_categories(
                compliance_categories
            )

            compliance_chart.height = 7
            compliance_chart.width = 12

            dashboard.add_chart(
                compliance_chart,
                "A32"
            )


            # =================================================
            # DASHBOARD FORMATTING
            # =================================================

            for column in range(1, 9):

                dashboard.column_dimensions[
                    get_column_letter(column)
                ].width = 20

            dashboard.freeze_panes = "A4"


            # =================================================
            # FORMAT ALL WORKSHEETS
            # =================================================

            for worksheet in writer.sheets.values():

                if worksheet.title != "Governance Dashboard":

                    worksheet.freeze_panes = "A2"

                    worksheet.auto_filter.ref = (
                        worksheet.dimensions
                    )

                    for column in worksheet.columns:

                        max_length = 0

                        column_letter = (
                            column[0].column_letter
                        )

                        for cell in column:

                            if cell.value is not None:

                                max_length = max(
                                    max_length,
                                    len(str(cell.value))
                                )

                        worksheet.column_dimensions[
                            column_letter
                        ].width = min(
                            max_length + 3,
                            55
                        )


        # ====================================================
        # FINAL REPORT SUMMARY
        # ====================================================

        print("\n======================================")
        print("AQUAPURE GOVERNANCE REPORT")
        print("======================================")

        print("Report generated successfully!")

        print("File:", filename)

        print("Risk records:", len(risks))

        print("Incident records:", len(incidents))

        print("Compliance records:", len(compliance))

        print("Audit records:", len(audit_logs))

        print("Data governance records:", len(governance))

        print("Data purpose records:", len(data_purpose))

        print("Implemented:", implemented)

        print("In Progress:", in_progress)

        print("Not Started:", not_started)

        print("Needs Review:", needs_review)

        print(
            "Compliance progress:",
            str(round(progress, 2)) + "%"
        )

        print("Worksheets generated: 8")

        print("Dashboard charts generated: 3")

        print("======================================")


    finally:

        conn.close()


# ============================================================
# RUN REPORT
# ============================================================

if __name__ == "__main__":

    generate_consolidated_report()
