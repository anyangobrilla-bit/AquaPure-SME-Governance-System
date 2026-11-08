import sqlite3
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList

from database import connect_db


FILENAME = "AquaPure_Management_Dashboard.xlsx"


def get_dashboard_data():
    """Retrieve governance information from the existing SQLite database."""

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 1. Risk register
        cursor.execute("SELECT risk_score FROM risks")
        risk_scores = [row[0] for row in cursor.fetchall()]

        risk_levels = {
            "Low": 0,
            "Medium": 0,
            "High": 0,
            "Critical": 0
        }

        for score in risk_scores:
            if score <= 5:
                risk_levels["Low"] += 1
            elif score <= 10:
                risk_levels["Medium"] += 1
            elif score <= 15:
                risk_levels["High"] += 1
            else:
                risk_levels["Critical"] += 1

        # 2. Incident register
        cursor.execute("SELECT status FROM incidents")
        incident_statuses = [
            row[0].upper() for row in cursor.fetchall()
        ]

        incident_counts = {
            "OPEN": incident_statuses.count("OPEN"),
            "INVESTIGATING": incident_statuses.count("INVESTIGATING"),
            "RESOLVED": incident_statuses.count("RESOLVED")
        }

        # 3. Compliance register
        cursor.execute("SELECT status FROM compliance_checks")
        compliance_statuses = [
            row[0] for row in cursor.fetchall()
        ]

        compliance_counts = {
            "Implemented": compliance_statuses.count("Implemented"),
            "In Progress": compliance_statuses.count("In Progress"),
            "Not Started": compliance_statuses.count("Not Started"),
            "Needs Review": compliance_statuses.count("Needs Review")
        }

        # 4. Data governance register
        cursor.execute("SELECT classification FROM governance_records")
        classifications = [
            row[0].upper() for row in cursor.fetchall()
        ]

        classification_counts = {
            "PUBLIC": classifications.count("PUBLIC"),
            "INTERNAL": classifications.count("INTERNAL"),
            "CONFIDENTIAL": classifications.count("CONFIDENTIAL"),
            "RESTRICTED": classifications.count("RESTRICTED")
        }

        # 5. Data purpose register
        cursor.execute("SELECT approval_status FROM data_purpose_register")
        approval_statuses = [
            row[0] for row in cursor.fetchall()
        ]

        approval_counts = {
            "Approved": approval_statuses.count("Approved"),
            "Pending Approval": approval_statuses.count("Pending Approval"),
            "Needs Review": approval_statuses.count("Needs Review")
        }

        # Calculate management indicators
        total_risks = len(risk_scores)
        serious_risks = risk_levels["High"] + risk_levels["Critical"]

        total_incidents = len(incident_statuses)
        unresolved_incidents = (
            incident_counts["OPEN"] + incident_counts["INVESTIGATING"]
        )

        total_compliance = len(compliance_statuses)
        implemented = compliance_counts["Implemented"]

        compliance_progress = (
            (implemented / total_compliance) * 100
            if total_compliance > 0 else 0
        )

        total_governance = len(classifications)
        pending_approvals = approval_counts["Pending Approval"]

        return {
            "risk_levels": risk_levels,
            "incident_counts": incident_counts,
            "compliance_counts": compliance_counts,
            "classification_counts": classification_counts,
            "approval_counts": approval_counts,
            "total_risks": total_risks,
            "serious_risks": serious_risks,
            "total_incidents": total_incidents,
            "unresolved_incidents": unresolved_incidents,
            "total_compliance": total_compliance,
            "implemented": implemented,
            "compliance_progress": compliance_progress,
            "total_governance": total_governance,
            "pending_approvals": pending_approvals
        }

    finally:
        conn.close()


def add_summary_table(ws, start_column, start_row, title, values):
    """Write chart data into the supporting worksheet."""

    ws.cell(start_row, start_column, title)
    ws.cell(start_row + 1, start_column, "Category")
    ws.cell(start_row + 1, start_column + 1, "Count")

    for index, (category, count) in enumerate(values.items(), start=2):
        ws.cell(start_row + index, start_column, category)
        ws.cell(start_row + index, start_column + 1, count)

    return start_row + 1, start_row + len(values) + 1


def add_bar_chart(ws, data_ws, title, position, column, first_row, last_row):
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = title
    chart.y_axis.title = "Number of Records"
    chart.x_axis.title = "Category"
    chart.height = 8
    chart.width = 14

    data = Reference(
        data_ws,
        min_col=column + 1,
        min_row=first_row,
        max_row=last_row
    )

    categories = Reference(
        data_ws,
        min_col=column,
        min_row=first_row + 1,
        max_row=last_row
    )

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.legend = None

    ws.add_chart(chart, position)


def add_pie_chart(ws, data_ws, title, position, column, first_row, last_row):
    chart = PieChart()
    chart.title = title
    chart.height = 8
    chart.width = 14

    data = Reference(
        data_ws,
        min_col=column + 1,
        min_row=first_row,
        max_row=last_row
    )

    categories = Reference(
        data_ws,
        min_col=column,
        min_row=first_row + 1,
        max_row=last_row
    )

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showPercent = True
    chart.dataLabels.showLeaderLines = True

    ws.add_chart(chart, position)


def generate_management_dashboard():
    print("\nGenerating AquaPure Management Dashboard...")

    data = get_dashboard_data()

    workbook = Workbook()

    dashboard = workbook.active
    dashboard.title = "Management Dashboard"

    data_ws = workbook.create_sheet("Dashboard Data")

    # Dashboard title
    dashboard.merge_cells("A1:N1")
    dashboard["A1"] = "AQUAPURE MANAGEMENT DASHBOARD"
    dashboard["A1"].font = Font(
        name="Arial",
        size=18,
        bold=True,
        color="FFFFFF"
    )
    dashboard["A1"].fill = PatternFill(
        "solid",
        fgColor="17365D"
    )
    dashboard["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center"
    )
    dashboard.row_dimensions[1].height = 35

    dashboard.merge_cells("A2:N2")
    dashboard["A2"] = (
        "SME Data Governance and Cybersecurity Performance Overview"
    )
    dashboard["A2"].font = Font(
        italic=True,
        color="666666",
        size=11
    )
    dashboard["A2"].alignment = Alignment(horizontal="center")

    dashboard.merge_cells("A3:N3")
    dashboard["A3"] = (
        "Report generated: " +
        datetime.now().strftime("%d %B %Y, %H:%M")
    )
    dashboard["A3"].alignment = Alignment(horizontal="center")
    dashboard["A3"].font = Font(size=9, color="666666")

    # KPI cards
    kpis = [
        ("A5", "C5", "A6", "C7", "TOTAL RISKS", data["total_risks"]),
        ("E5", "G5", "E6", "G7", "HIGH / CRITICAL RISKS", data["serious_risks"]),
        ("I5", "K5", "I6", "K7", "UNRESOLVED INCIDENTS", data["unresolved_incidents"]),
        ("M5", "N5", "M6", "N7", "COMPLIANCE PROGRESS", f'{data["compliance_progress"]:.1f}%'),
        ("A8", "C8", "A9", "C10", "TOTAL INCIDENTS", data["total_incidents"]),
        ("E8", "G8", "E9", "G10", "COMPLIANCE REQUIREMENTS", data["total_compliance"]),
        ("I8", "K8", "I9", "K10", "GOVERNANCE RECORDS", data["total_governance"]),
        ("M8", "N8", "M9", "N10", "PENDING APPROVALS", data["pending_approvals"])
    ]

    for label_start, label_end, value_start, value_end, label, value in kpis:
        dashboard.merge_cells(f"{label_start}:{label_end}")
        dashboard.merge_cells(f"{value_start}:{value_end}")

        label_cell = dashboard[label_start]
        label_cell.value = label
        label_cell.font = Font(bold=True, color="FFFFFF", size=9)
        label_cell.fill = PatternFill("solid", fgColor="305496")
        label_cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

        value_cell = dashboard[value_start]
        value_cell.value = value
        value_cell.font = Font(bold=True, size=19, color="17365D")
        value_cell.fill = PatternFill("solid", fgColor="D9EAF7")
        value_cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # Supporting chart data
    chart_tables = [
        (1, 1, "Risk Severity", data["risk_levels"]),
        (4, 1, "Incident Status", data["incident_counts"]),
        (7, 1, "Compliance Status", data["compliance_counts"]),
        (10, 1, "Data Classification", data["classification_counts"]),
        (13, 1, "Data Purpose Approval", data["approval_counts"])
    ]

    chart_ranges = {}

    for column, row, title, values in chart_tables:
        first_row, last_row = add_summary_table(
            data_ws,
            column,
            row,
            title,
            values
        )
        chart_ranges[title] = (column, first_row, last_row)

    # Create five charts
    column, first_row, last_row = chart_ranges["Risk Severity"]
    add_bar_chart(
        dashboard, data_ws, "Risk Severity Distribution",
        "A12", column, first_row, last_row
    )

    column, first_row, last_row = chart_ranges["Incident Status"]
    add_bar_chart(
        dashboard, data_ws, "Incident Status Overview",
        "H12", column, first_row, last_row
    )

    column, first_row, last_row = chart_ranges["Compliance Status"]
    add_bar_chart(
        dashboard, data_ws, "Compliance Implementation Status",
        "A28", column, first_row, last_row
    )

    column, first_row, last_row = chart_ranges["Data Classification"]
    add_pie_chart(
        dashboard, data_ws, "Data Classification Distribution",
        "H28", column, first_row, last_row
    )

    column, first_row, last_row = chart_ranges["Data Purpose Approval"]
    add_pie_chart(
        dashboard, data_ws, "Data Purpose Approval Status",
        "A44", column, first_row, last_row
    )

    # Formatting
    for column_letter in "ABCDEFGHIJKLMN":
        dashboard.column_dimensions[column_letter].width = 13

    dashboard.freeze_panes = "A4"
    dashboard.sheet_view.showGridLines = False

    data_ws.sheet_state = "hidden"

    # Save workbook
    workbook.save(FILENAME)

    print("\n======================================")
    print("AQUAPURE MANAGEMENT DASHBOARD")
    print("======================================")
    print("Dashboard generated successfully!")
    print("File:", FILENAME)
    print("Total risks:", data["total_risks"])
    print("High/Critical risks:", data["serious_risks"])
    print("Total incidents:", data["total_incidents"])
    print("Unresolved incidents:", data["unresolved_incidents"])
    print("Compliance progress:", f'{data["compliance_progress"]:.1f}%')
    print("Governance records:", data["total_governance"])
    print("Pending data purpose approvals:", data["pending_approvals"])
    print("Charts generated: 5")
    print("======================================")


if __name__ == "__main__":
    generate_management_dashboard()