from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from database import connect_db

FILENAME = "AquaPure_Management_Dashboard.xlsx"


def get_management_data():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT risk_score FROM risks")
        scores = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT status FROM incidents")
        incidents = [row[0].upper() for row in cursor.fetchall()]

        cursor.execute("SELECT status FROM compliance_checks")
        compliance = [row[0] for row in cursor.fetchall()]

        cursor.execute(
            "SELECT classification FROM governance_records"
        )
        classifications = [
            row[0].upper() for row in cursor.fetchall()
        ]

        cursor.execute(
            "SELECT approval_status FROM data_purpose_register"
        )
        approvals = [row[0] for row in cursor.fetchall()]

        return {
            "total_risks": len(scores),
            "critical_risks": sum(score >= 16 for score in scores),
            "high_risks": sum(11 <= score <= 15 for score in scores),
            "total_incidents": len(incidents),
            "unresolved_incidents": sum(
                status in ("OPEN", "INVESTIGATING")
                for status in incidents
            ),
            "total_compliance": len(compliance),
            "implemented": compliance.count("Implemented"),
            "in_progress": compliance.count("In Progress"),
            "not_started": compliance.count("Not Started"),
            "needs_review": compliance.count("Needs Review"),
            "total_governance": len(classifications),
            "restricted_records": classifications.count("RESTRICTED"),
            "confidential_records": classifications.count("CONFIDENTIAL"),
            "total_approvals": len(approvals),
            "pending_approvals": approvals.count("Pending Approval"),
            "approved": approvals.count("Approved"),
            "approvals_needing_review": approvals.count("Needs Review")
        }

    finally:
        conn.close()


def generate_executive_summary():
    data = get_management_data()

    workbook = load_workbook(FILENAME)

    if "Executive Summary" in workbook.sheetnames:
        del workbook["Executive Summary"]

    ws = workbook.create_sheet("Executive Summary", 0)

    # Title
    ws.merge_cells("A1:F1")
    ws["A1"] = "AQUAPURE MANAGEMENT EXECUTIVE SUMMARY"
    ws["A1"].font = Font(
        name="Arial", size=17, bold=True, color="FFFFFF"
    )
    ws["A1"].fill = PatternFill("solid", fgColor="17365D")
    ws["A1"].alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 35

    ws.merge_cells("A2:F2")
    ws["A2"] = (
        "Data Governance and Cybersecurity Performance Review"
    )
    ws["A2"].font = Font(italic=True, color="666666")
    ws["A2"].alignment = Alignment(horizontal="center")

    # Management overview
    ws["A4"] = "1. MANAGEMENT PERFORMANCE OVERVIEW"
    ws["A4"].font = Font(bold=True, size=12, color="17365D")

    metrics = [
        ("Total Identified Risks", data["total_risks"]),
        ("Critical Risks", data["critical_risks"]),
        ("High Risks", data["high_risks"]),
        ("Total Incidents", data["total_incidents"]),
        ("Unresolved Incidents", data["unresolved_incidents"]),
        ("Total Compliance Requirements", data["total_compliance"]),
        ("Implemented Requirements", data["implemented"]),
        ("Requirements In Progress", data["in_progress"]),
        ("Requirements Not Started", data["not_started"]),
        ("Governance Records", data["total_governance"]),
        ("Confidential Records", data["confidential_records"]),
        ("Restricted Records", data["restricted_records"]),
        ("Data Purpose Records", data["total_approvals"]),
        ("Pending Purpose Approvals", data["pending_approvals"]),
        ("Approved Purpose Records", data["approved"])
    ]

    ws["A5"] = "Management Indicator"
    ws["B5"] = "Current Result"

    for cell in ws[5][:2]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="305496")

    for row, (label, value) in enumerate(metrics, start=6):
        ws.cell(row, 1, label)
        ws.cell(row, 2, value)

    # Executive assessment
    ws["D4"] = "2. EXECUTIVE ASSESSMENT"
    ws["D4"].font = Font(bold=True, size=12, color="17365D")

    assessments = [
        (
            "Risk Management",
            f'{data["critical_risks"]} critical and '
            f'{data["high_risks"]} high risks require management attention.'
        ),
        (
            "Incident Management",
            f'{data["unresolved_incidents"]} incidents remain unresolved '
            f'out of {data["total_incidents"]} recorded.'
        ),
        (
            "Regulatory Compliance",
            f'{data["implemented"]} of {data["total_compliance"]} '
            'requirements are currently implemented.'
        ),
        (
            "Data Governance",
            f'{data["total_governance"]} data categories are recorded, '
            'including confidential and restricted information.'
        ),
        (
            "Data Purpose Approval",
            f'{data["pending_approvals"]} of {data["total_approvals"]} '
            'data purpose records are awaiting approval.'
        )
    ]

    current_row = 5

    for heading, description in assessments:
        ws.cell(current_row, 4, heading)
        ws.cell(current_row, 4).font = Font(bold=True, color="305496")

        ws.merge_cells(
            start_row=current_row,
            start_column=5,
            end_row=current_row,
            end_column=6
        )
        ws.cell(current_row, 5, description)
        ws.cell(current_row, 5).alignment = Alignment(
            wrap_text=True, vertical="top"
        )
        ws.row_dimensions[current_row].height = 42

        current_row += 2

    # Management recommendations
    ws["A23"] = "3. PRIORITY MANAGEMENT RECOMMENDATIONS"
    ws["A23"].font = Font(bold=True, size=12, color="17365D")

    recommendations = [
        (
            "Priority 1 - Risk Reduction",
            "Review the two critical risks first, followed by the "
            "high risks. Assign responsible owners, treatment actions "
            "and review dates."
        ),
        (
            "Priority 2 - Incident Resolution",
            "Continue investigating unresolved incidents, document "
            "response actions and record evidence before closing them."
        ),
        (
            "Priority 3 - Compliance Implementation",
            "Prioritise the five requirements not yet started. "
            "Assign responsible persons and retain evidence before "
            "marking controls as implemented."
        ),
        (
            "Priority 4 - Data Purpose Approval",
            "Review the three pending data purpose records, prepare "
            "the required supporting documents and obtain formal approval."
        ),
        (
            "Priority 5 - Data Access and Protection",
            "Review access to confidential and restricted records. "
            "Confirm that only authorised personnel can access them."
        ),
        (
            "Priority 6 - Continuous Monitoring",
            "Conduct periodic reviews of risks, incidents, audit logs, "
            "compliance requirements and data governance records."
        )
    ]

    row = 24

    for heading, recommendation in recommendations:
        ws.cell(row, 1, heading)
        ws.cell(row, 1).font = Font(bold=True, color="305496")

        ws.merge_cells(
            start_row=row,
            start_column=2,
            end_row=row,
            end_column=6
        )

        ws.cell(row, 2, recommendation)
        ws.cell(row, 2).alignment = Alignment(
            wrap_text=True, vertical="top"
        )

        ws.row_dimensions[row].height = 42
        row += 2

    # Disclaimer
    ws.merge_cells(start_row=row + 1, start_column=1,
                   end_row=row + 2, end_column=6)

    ws.cell(
        row + 1, 1,
        "NOTE: This dashboard is a management decision-support "
        "prototype based on records currently entered in the "
        "AquaPure database. It does not independently establish "
        "legal compliance or ISO/IEC 27001 certification."
    )
    ws.cell(row + 1, 1).font = Font(
        italic=True, size=9, color="666666"
    )
    ws.cell(row + 1, 1).alignment = Alignment(
        wrap_text=True, vertical="center"
    )

    # General formatting
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 4
    ws.column_dimensions["D"].width = 27
    ws.column_dimensions["E"].width = 30
    ws.column_dimensions["F"].width = 30

    ws.freeze_panes = "A5"
    ws.sheet_view.showGridLines = False

    for row_cells in ws.iter_rows():
        for cell in row_cells:
            cell.alignment = Alignment(
                horizontal="left",
                vertical="center",
                wrap_text=True
            )

    # Restore important title formatting after general alignment
    ws["A1"].alignment = Alignment(horizontal="center")
    ws["A2"].alignment = Alignment(horizontal="center")

    workbook.save(FILENAME)

    print("\nExecutive Summary added successfully!")
    print("Workbook:", FILENAME)
    print("New worksheet: Executive Summary")
    print("Management recommendations: 6")


if __name__ == "__main__":
    generate_executive_summary()