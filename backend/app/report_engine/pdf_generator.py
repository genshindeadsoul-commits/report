from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from typing import Dict, Any
import io

class PDFGenerator:
    """
    Generates a professional, brandable A4 PDF report card.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor(config.get("primary_color", "#1F4E8C"))

    def generate(self, report_data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # 1. Header
        header_style = ParagraphStyle(
            "HeaderStyle",
            parent=self.styles["Heading1"],
            alignment=1, # Center
            textColor=self.primary_color,
            fontSize=22
        )
        elements.append(Paragraph(self.config["school_name"].upper(), header_style))
        elements.append(Paragraph(f"Academic Year: {report_data['config']['academic_year']}", self.styles["Heading3"]))
        elements.append(Spacer(1, 20))

        # 2. Student Info Card
        student = report_data["student"]
        info_data = [
            [f"Student Name: {student['name']}", f"Roll No: {student['roll']}"],
            [f"Class: {student['class']}", f"Section: {student['section']}"]
        ]
        info_table = Table(info_data, colWidths=[250, 250])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # 3. Academic Table
        table_data = [["Subject", "Max Marks", "Obtained", "Percentage", "Grade"]]
        for sub in report_data["subjects"]:
            table_data.append([
                sub["subject"],
                sub["max_marks"],
                sub["marks"],
                f"{sub['percentage']}%",
                sub["grade"]
            ])

        # Add Total Row
        overall = report_data["overall"]
        table_data.append(["TOTAL", overall["total_max"], overall["total_marks"], f"{overall['overall_percentage']}%", overall["overall_grade"]])

        academic_table = Table(table_data, colWidths=[150, 80, 80, 100, 80])
        academic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(academic_table)
        elements.append(Spacer(1, 20))

        # 4. Attendance and Observation
        att = report_data["attendance"]
        obs_text = f"Observation: {report_data.get('observation', 'No remarks provided.')}"

        elements.append(Paragraph(f"Attendance: {att['percentage']}% ({att['present_days']}/{att['working_days']} days)", self.styles["Normal"]))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(obs_text, self.styles["Italic"]))

        # 5. Signature Line
        elements.append(Spacer(1, 40))
        sig_data = [["", "Principal Signature", "Class Teacher Signature"]]
        sig_table = Table(sig_data, colWidths=[200, 150, 150])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (1, 0), (2, 0), 1, colors.black),
        ]))
        elements.append(sig_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes


# ---------------------------------------------------------------------------
# Module-level function wrappers, kept for the same reason as in
# calculations.py: app/report_engine/__init__.py and app/routes/reports.py
# expect generate_pdf / generate_combined_pdf functions from an earlier,
# function-based version of this module. They now delegate to the
# PDFGenerator class instead of duplicating PDF layout code.
# ---------------------------------------------------------------------------

def generate_pdf(report_data: Dict[str, Any]) -> bytes:
    config = report_data.get("config", {})
    return PDFGenerator(config).generate(report_data)


def generate_combined_pdf(report_data_list) -> bytes:
    """Concatenates one PDF per student into a single multi-page PDF."""
    from pypdf import PdfWriter, PdfReader

    writer = PdfWriter()
    for report_data in report_data_list:
        pdf_bytes = generate_pdf(report_data)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()
