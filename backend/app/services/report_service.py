"""
The glue between raw StudentInput data and the report_engine's pure
functions. build_report() produces one dict — report_data — that both the
DOCX and PDF generators consume directly, and that the frontend preview
screen can also be given as JSON.
"""

from typing import Dict
from app.models.schemas import StudentInput
from app.report_engine import (
    calculate_total_marks, calculate_max_marks, calculate_percentage,
    calculate_attendance, calculate_grade, calculate_subject_grades,
    build_insights, generate_remark, DEFAULT_CONFIG,
)
from app.report_engine.ai_enhancer import (
    is_ai_available, build_ai_payload, enhance_remark_with_ai,
)


def build_report(student: StudentInput, use_ai: bool = False, config=DEFAULT_CONFIG) -> Dict:
    subject_max = student.subject_max_marks or {s: 100 for s in student.subject_marks}

    subject_rows = calculate_subject_grades(student.subject_marks, subject_max, config)
    total_marks = calculate_total_marks(student.subject_marks)
    max_marks = calculate_max_marks(subject_max)
    percentage = calculate_percentage(total_marks, max_marks)
    grade = calculate_grade(percentage, config)
    attendance_pct = calculate_attendance(student.present_days, student.working_days)

    insights = build_insights(
        subject_rows, percentage, attendance_pct,
        previous_percentage=student.previous_percentage, config=config,
    )

    base_remark = generate_remark(
        name=student.name,
        percentage=percentage,
        strong_subject=insights["strongest_subject"]["subject"],
        focus_subject=insights["focus_subject"]["subject"],
        attendance_pct=attendance_pct,
        overall_performance=insights["overall_performance"],
        participation=student.class_participation,
        behaviour=student.behaviour,
        homework=student.homework,
        teacher_remark=student.teacher_remark,
    )

    observation = base_remark
    if use_ai and is_ai_available():
        payload = build_ai_payload(
            student_name=student.name, percentage=percentage, grade=grade,
            attendance=attendance_pct,
            strong_subject=insights["strongest_subject"]["subject"],
            focus_subject=insights["focus_subject"]["subject"],
            performance=insights["overall_performance"],
            participation=student.class_participation, behaviour=student.behaviour,
            homework=student.homework, teacher_remark=student.teacher_remark,
        )
        observation = enhance_remark_with_ai(base_remark, payload)

    absent_days = max(student.working_days - student.present_days, 0)

    return {
        "student": {
            "name": student.name,
            "class_": student.class_,
            "section": student.section,
            "roll_number": student.roll_number,
            "academic_year": student.academic_year,
        },
        "summary": {
            "total_marks": total_marks,
            "max_marks": max_marks,
            "percentage": percentage,
            "grade": grade,
            "performance": insights["overall_performance"],
        },
        "subjects": subject_rows,
        "insights": insights,
        "attendance": {
            "working_days": student.working_days,
            "present_days": student.present_days,
            "absent_days": absent_days,
            "percentage": attendance_pct,
        },
        "assessment": {
            "Academic Performance": student.academic_performance,
            "Class Participation": student.class_participation,
            "Behaviour": student.behaviour,
            "Homework": student.homework,
            "Communication": "Good",
        },
        "observation": observation,
        "editable_remark": base_remark,  # what the teacher sees/edits before final generation
        "config": {
            "school_name": config.school_name,
            "academic_year": config.academic_year,
        },
    }
