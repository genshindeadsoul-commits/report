"""
Generates a real, editable .docx report using python-docx. The teacher can
open this file in Word and edit it directly. Layout mirrors the PDF design
(header, student info card, summary, marks table, insights, attendance,
teacher assessment, observation, signatures) using tables for card-style
layout since python-docx has no native "card" concept.
"""

import io
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

PRIMARY_RGB = RGBColor(0x1F, 0x4E, 0x8C)
LIGHT_RGB = "EAF1FB"


def _shade_cell(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _set_cell_text(cell, text, bold=False, size=10, color=None, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align:
        p.alignment = align
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color


def _add_heading(doc, text, size=13):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(size)
    run.font.color.rgb = PRIMARY_RGB
    p.space_before = Pt(12)
    p.space_after = Pt(4)
    return p


def generate_docx(report_data: dict) -> bytes:
    """report_data is the fully-assembled dict from report_service.build_report()."""
    doc = Document()

    section = doc.sections[0]
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)

    student = report_data["student"]
    summary = report_data["summary"]
    subjects = report_data["subjects"]
    insights = report_data["insights"]
    attendance = report_data["attendance"]
    assessment = report_data["assessment"]
    observation = report_data["observation"]
    config = report_data["config"]

    # ---- Header ----
    h1 = doc.add_paragraph()
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = h1.add_run(config["school_name"])
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = PRIMARY_RGB

    h2 = doc.add_paragraph()
    h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = h2.add_run("STUDENT PERFORMANCE REPORT")
    run.bold = True
    run.font.size = Pt(13)

    h3 = doc.add_paragraph()
    h3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = h3.add_run(f"Academic Year {config['academic_year']}")
    run.font.size = Pt(10)
    run.italic = True

    doc.add_paragraph()

    # ---- Student information card ----
    info_table = doc.add_table(rows=3, cols=4)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_pairs = [
        ("Student Name", student["name"]), ("Class", student["class_"]),
        ("Section", student["section"]), ("Roll Number", student["roll_number"]),
        ("Academic Year", student["academic_year"]), ("Report Type", "Individual"),
    ]
    for i, (label, value) in enumerate(info_pairs):
        row, col = divmod(i, 2)
        cell = info_table.cell(row, col * 2)
        _shade_cell(cell, LIGHT_RGB)
        _set_cell_text(cell, label, bold=True, size=9)
        vcell = info_table.cell(row, col * 2 + 1)
        _set_cell_text(vcell, value, size=10)

    doc.add_paragraph()

    # ---- Performance summary cards ----
    _add_heading(doc, "Performance Summary")
    summary_table = doc.add_table(rows=2, cols=4)
    summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cards = [
        (f"{summary['percentage']}%", "Overall Percentage"),
        (summary["grade"], "Overall Grade"),
        (f"{attendance['percentage']}%", "Attendance"),
        (summary["performance"].upper(), "Performance"),
    ]
    for i, (value, label) in enumerate(cards):
        vcell = summary_table.cell(0, i)
        _shade_cell(vcell, LIGHT_RGB)
        _set_cell_text(vcell, value, bold=True, size=14, color=PRIMARY_RGB, align=WD_ALIGN_PARAGRAPH.CENTER)
        lcell = summary_table.cell(1, i)
        _set_cell_text(lcell, label, size=8, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph()

    # ---- Academic performance table ----
    _add_heading(doc, "Academic Performance")
    subj_table = doc.add_table(rows=1 + len(subjects), cols=4)
    subj_table.style = "Light Grid Accent 1"
    hdr = subj_table.rows[0].cells
    for i, h in enumerate(["Subject", "Marks", "Grade", "Performance"]):
        _shade_cell(hdr[i], LIGHT_RGB)
        _set_cell_text(hdr[i], h, bold=True, size=10)
    for r, row in enumerate(subjects, start=1):
        cells = subj_table.rows[r].cells
        _set_cell_text(cells[0], row["subject"], size=10)
        _set_cell_text(cells[1], f"{row['marks']}/{row['max_marks']}", size=10)
        _set_cell_text(cells[2], row["grade"], size=10)
        _set_cell_text(cells[3], row["performance"], size=10)

    totals_p = doc.add_paragraph()
    totals_p.add_run(
        f"Total Marks: {summary['total_marks']}/{summary['max_marks']}   |   "
        f"Percentage: {summary['percentage']}%   |   Overall Grade: {summary['grade']}"
    ).bold = True

    doc.add_paragraph()

    # ---- Automatic insights ----
    _add_heading(doc, "Automatic Performance Insights")
    insight_lines = [
        f"\u2605 Strongest Subject: {insights['strongest_subject']['subject']} — {insights['strongest_subject']['percentage']}%",
        f"\u25CF Focus Area: {insights['focus_subject']['subject']} — {insights['focus_subject']['percentage']}%",
        f"\u2191 Overall Assessment: {insights['overall_performance']} academic performance",
        f"\u2713 Attendance: {attendance['percentage']}% — {insights['attendance_analysis']}",
    ]
    if insights.get("improvement"):
        imp = insights["improvement"]
        sign = "+" if imp["difference"] >= 0 else ""
        insight_lines.append(
            f"\u2192 Improvement: {imp['status']} ({sign}{imp['difference']} percentage points vs previous term)"
        )
    for line in insight_lines:
        doc.add_paragraph(line)

    doc.add_paragraph()

    # ---- Attendance ----
    _add_heading(doc, "Attendance")
    att_table = doc.add_table(rows=2, cols=4)
    att_vals = [
        (attendance["working_days"], "Working Days"),
        (attendance["present_days"], "Present"),
        (attendance["absent_days"], "Absent"),
        (f"{attendance['percentage']}%", "Attendance %"),
    ]
    for i, (value, label) in enumerate(att_vals):
        vcell = att_table.cell(0, i)
        _shade_cell(vcell, LIGHT_RGB)
        _set_cell_text(vcell, value, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
        lcell = att_table.cell(1, i)
        _set_cell_text(lcell, label, size=8, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph()

    # ---- Teacher assessment ----
    _add_heading(doc, "Teacher Assessment")
    ta_table = doc.add_table(rows=len(assessment), cols=2)
    ta_table.style = "Light Grid Accent 1"
    for i, (label, value) in enumerate(assessment.items()):
        cells = ta_table.rows[i].cells
        _shade_cell(cells[0], LIGHT_RGB)
        _set_cell_text(cells[0], label, bold=True, size=10)
        _set_cell_text(cells[1], value, size=10)

    doc.add_paragraph()

    # ---- Teacher's observation ----
    _add_heading(doc, "Teacher's Observation")
    obs_table = doc.add_table(rows=1, cols=1)
    obs_cell = obs_table.cell(0, 0)
    _shade_cell(obs_cell, LIGHT_RGB)
    _set_cell_text(obs_cell, observation, size=10.5)

    doc.add_paragraph()
    doc.add_paragraph()

    # ---- Signatures ----
    sig_table = doc.add_table(rows=2, cols=3)
    for i, label in enumerate(["Teacher Signature", "Class Teacher", "Date"]):
        cells = sig_table.rows[0].cells
        _set_cell_text(cells[i], "_" * 20, size=10)
        cells2 = sig_table.rows[1].cells
        _set_cell_text(cells2[i], label, size=9, bold=True)

    # ---- Footer with page number ----
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run(config["school_name"] + " — Generated Report")
    fp.runs[0].font.size = Pt(8)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
