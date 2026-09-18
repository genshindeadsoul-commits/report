"""
Reads teacher-uploaded Excel files, validates them, and converts valid rows
into StudentInput objects the report engine can consume. Also builds the
downloadable Excel template.
"""

import io
from typing import List, Tuple
import pandas as pd

from app.models.schemas import StudentInput, ValidationIssue, BulkUploadResult

SUBJECT_COLUMNS = ["English", "Mathematics", "Science", "Social Science", "Hindi"]

REQUIRED_COLUMNS = [
    "Student Name", "Class", "Section", "Roll Number", "Academic Year",
    *SUBJECT_COLUMNS,
    "Working Days", "Present Days", "Absent Days",
    "Academic Performance", "Class Participation", "Behaviour", "Homework",
    "Teacher Remark",
]

DEFAULT_MAX_MARKS = 100


class ExcelValidationError(Exception):
    """Raised when the file itself can't be processed (missing columns,
    empty file, corrupted file) — as opposed to per-row data issues, which
    are collected instead of raised."""
    def __init__(self, message: str, missing_columns: List[str] = None):
        super().__init__(message)
        self.message = message
        self.missing_columns = missing_columns or []


def read_excel(file_bytes: bytes) -> pd.DataFrame:
    try:
        df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        raise ExcelValidationError(
            "This file could not be read. Please make sure it is a valid, "
            "uncorrupted .xlsx file and try again."
        ) from e

    if df.empty:
        raise ExcelValidationError(
            "The uploaded file has no student rows. Please add students "
            "using the standard template and re-upload."
        )
    return df


def validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ExcelValidationError(
            "The uploaded file is missing required columns. Please download "
            "the standard Excel template and try again.",
            missing_columns=missing,
        )


def _row_to_student(row: pd.Series, row_num: int) -> Tuple[StudentInput, List[ValidationIssue]]:
    issues: List[ValidationIssue] = []
    name = str(row.get("Student Name", "")).strip()

    if not name or name.lower() == "nan":
        issues.append(ValidationIssue(row=row_num, field="Student Name", message="Missing student name"))
        name = name or f"Row {row_num}"

    subject_marks = {}
    subject_max_marks = {}
    for subj in SUBJECT_COLUMNS:
        raw = row.get(subj)
        try:
            marks = float(raw)
        except (TypeError, ValueError):
            issues.append(ValidationIssue(row=row_num, student_name=name, field=subj,
                                           message=f"Invalid or missing marks for {subj}"))
            marks = 0.0
        if marks < 0:
            issues.append(ValidationIssue(row=row_num, student_name=name, field=subj,
                                           message=f"{subj} marks cannot be negative"))
            marks = 0.0
        if marks > DEFAULT_MAX_MARKS:
            issues.append(ValidationIssue(row=row_num, student_name=name, field=subj,
                                           message=f"{subj} marks ({marks}) exceed maximum marks ({DEFAULT_MAX_MARKS})"))
            marks = DEFAULT_MAX_MARKS
        subject_marks[subj] = marks
        subject_max_marks[subj] = DEFAULT_MAX_MARKS

    try:
        working_days = float(row.get("Working Days"))
        if working_days <= 0:
            raise ValueError
    except (TypeError, ValueError):
        issues.append(ValidationIssue(row=row_num, student_name=name, field="Working Days",
                                       message="Invalid working days"))
        working_days = 1.0

    try:
        present_days = float(row.get("Present Days"))
    except (TypeError, ValueError):
        issues.append(ValidationIssue(row=row_num, student_name=name, field="Present Days",
                                       message="Invalid present days"))
        present_days = 0.0

    if present_days > working_days:
        issues.append(ValidationIssue(row=row_num, student_name=name, field="Present Days",
                                       message="Present days cannot exceed working days"))
        present_days = working_days

    student = StudentInput(
        name=name,
        **{"class": str(row.get("Class", "")).strip()},
        section=str(row.get("Section", "")).strip(),
        roll_number=str(row.get("Roll Number", "")).strip(),
        academic_year=str(row.get("Academic Year", "")).strip() or "2026-27",
        subject_marks=subject_marks,
        subject_max_marks=subject_max_marks,
        working_days=working_days,
        present_days=present_days,
        academic_performance=str(row.get("Academic Performance", "Good")).strip(),
        class_participation=str(row.get("Class Participation", "Active")).strip(),
        behaviour=str(row.get("Behaviour", "Good")).strip(),
        homework=str(row.get("Homework", "Usually Complete")).strip(),
        teacher_remark=(str(row.get("Teacher Remark", "")).strip() or None),
    )
    return student, issues


def process_excel(file_bytes: bytes) -> BulkUploadResult:
    df = read_excel(file_bytes)
    validate_columns(df)

    valid_students: List[StudentInput] = []
    all_issues: List[ValidationIssue] = []
    seen_roll_numbers = {}

    for idx, row in df.iterrows():
        row_num = idx + 2  # account for header row + 0-index
        student, issues = _row_to_student(row, row_num)

        roll = student.roll_number
        if roll and roll in seen_roll_numbers:
            issues.append(ValidationIssue(row=row_num, student_name=student.name,
                                           field="Roll Number",
                                           message=f"Duplicate roll number '{roll}' (also used in row {seen_roll_numbers[roll]})"))
        elif roll:
            seen_roll_numbers[roll] = row_num

        all_issues.extend(issues)
        valid_students.append(student)  # rows are auto-corrected + kept, with issues surfaced

    return BulkUploadResult(total_rows=len(df), valid_students=valid_students, errors=all_issues)


def build_template_bytes() -> bytes:
    """Builds the downloadable Excel template with example rows."""
    example_rows = [
        {
            "Student Name": "Aarav Sharma", "Class": "8", "Section": "A", "Roll Number": "801",
            "Academic Year": "2026-27", "English": 78, "Mathematics": 91, "Science": 86,
            "Social Science": 82, "Hindi": 88, "Working Days": 180, "Present Days": 170,
            "Absent Days": 10, "Academic Performance": "Very Good", "Class Participation": "Active",
            "Behaviour": "Excellent", "Homework": "Consistent",
            "Teacher Remark": "Good student, improve written English.",
        },
        {
            "Student Name": "Ananya Iyer", "Class": "8", "Section": "A", "Roll Number": "802",
            "Academic Year": "2026-27", "English": 65, "Mathematics": 58, "Science": 62,
            "Social Science": 60, "Hindi": 70, "Working Days": 180, "Present Days": 150,
            "Absent Days": 30, "Academic Performance": "Satisfactory", "Class Participation": "Moderate",
            "Behaviour": "Good", "Homework": "Sometimes Incomplete", "Teacher Remark": "",
        },
    ]
    df = pd.DataFrame(example_rows, columns=REQUIRED_COLUMNS)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Students")
    return buf.getvalue()
