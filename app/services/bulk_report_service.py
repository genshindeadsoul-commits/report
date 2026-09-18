import io
import zipfile
from typing import List, Dict, Any
from app.report_engine.calculations import CalculationEngine
from app.report_engine.pdf_generator import PDFGenerator

class BulkReportService:
    """
    Handles bulk PDF generation for multiple students.
    """

    def generate_zip(self, students_data: List[Dict[str, Any]], config: Dict[str, Any]) -> bytes:
        """
        Generates PDFs for all students and returns them as a ZIP archive.
        """
        buf = io.BytesIO()
        engine = CalculationEngine()
        pdf_gen = PDFGenerator(config)

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for student in students_data:
                # 1. Calculate metrics
                subject_marks = student.get("subject_marks", {})
                subject_max = student.get("subject_max_marks", {k: 100 for k in subject_marks})

                subject_metrics = []
                for sub, mark in subject_marks.items():
                    metrics = engine.calculate_subject_metrics(mark, subject_max.get(sub, 100))
                    subject_metrics.append({"subject": sub, **metrics})

                overall = engine.calculate_overall_metrics([
                    {"marks": m, "max_marks": mx}
                    for sub, m in subject_marks.items()
                    for mx in [subject_max.get(sub, 100)]
                ])

                attendance = engine.calculate_attendance_metrics(
                    student.get("present_days", 0), student.get("working_days", 0)
                )

                report_data = {
                    "student": {
                        "name": student["name"],
                        "class": student["class"],
                        "section": student["section"],
                        "roll": student["roll_number"]
                    },
                    "subjects": subject_metrics,
                    "overall": overall,
                    "attendance": attendance,
                    "observation": student.get("teacher_remark", "No remarks provided."),
                    "config": config
                }

                # 2. Generate PDF
                pdf_bytes = pdf_gen.generate(report_data)
                filename = f"{student['name'].replace(' ', '_')}.pdf"
                zf.writestr(filename, pdf_bytes)

        return buf.getvalue()
