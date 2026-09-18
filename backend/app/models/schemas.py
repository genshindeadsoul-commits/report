from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class StudentInput(BaseModel):
    """Raw input for a single student — from the form or one Excel row."""
    name: str
    class_: str = Field(alias="class")
    section: str
    roll_number: str
    academic_year: str = "2026-27"

    subject_marks: Dict[str, float]          # e.g. {"Mathematics": 91}
    subject_max_marks: Dict[str, float] = {}  # defaults to 100 per subject if omitted

    working_days: float
    present_days: float

    academic_performance: str = "Good"
    class_participation: str = "Active"
    behaviour: str = "Good"
    homework: str = "Usually Complete"
    communication: str = "Good"

    teacher_remark: Optional[str] = None
    previous_percentage: Optional[float] = None

    model_config = {"populate_by_name": True}

    @field_validator("subject_marks")
    @classmethod
    def not_empty(cls, v):
        if not v:
            raise ValueError("At least one subject mark is required")
        return v

    @field_validator("working_days")
    @classmethod
    def positive_working_days(cls, v):
        if v <= 0:
            raise ValueError("Working days must be greater than 0")
        return v


class ValidationIssue(BaseModel):
    row: Optional[int] = None
    student_name: Optional[str] = None
    field: str
    message: str


class BulkUploadResult(BaseModel):
    total_rows: int
    valid_students: List[StudentInput]
    errors: List[ValidationIssue]
