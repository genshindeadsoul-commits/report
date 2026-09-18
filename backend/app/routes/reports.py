"""
API routes. Kept thin on purpose — all real logic lives in
app/services and app/report_engine. Routes only: parse input, call a
service, translate errors into user-friendly HTTP responses, and stream
files back.
"""

import io
import zipfile
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from app.models.schemas import StudentInput
from app.report_engine.calculations import CalculationEngine
from app.services.report_service import build_report
from app.services.excel_service import (
    process_excel, build_template_bytes, ExcelValidationError,
)
from app.services.workbook_inspector import WorkbookInspector
from app.services.snapshot_service import ReportSnapshotService, ReportNotFoundError
from app.services.bulk_report_service import BulkReportService
from app.report_engine.pdf_generator import PDFGenerator
from app.report_engine import generate_docx, generate_pdf, generate_combined_pdf
from app.utils.auth import teacher_or_admin
from app.db import get_client, SupabaseNotConfiguredError

router = APIRouter()


def _safe_filename(name: str) -> str:
    return "_".join(name.strip().split()) or "student"


snapshot_service = ReportSnapshotService()
bulk_service = BulkReportService()

@router.get("/reports/view/{report_id}")
async def view_report(report_id: str, user=Depends(teacher_or_admin)):
    """Retrieves a persisted report card. Relies on Supabase RLS to ensure
    the user is authorized (see supabase/migrations/04_student_reports.sql)."""
    try:
        client = get_client()
    except SupabaseNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))

    result = client.table("student_reports").select("*").eq("id", report_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"No report found with id {report_id}")
    return result.data[0]

@router.post("/reports/snapshot")
async def create_snapshot(payload: Dict[str, Any], report_id: str, user=Depends(teacher_or_admin)):
    try:
        return snapshot_service.create_snapshot(report_id, payload, user.get("sub", "unknown"))
    except ReportNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SupabaseNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reports/publish/{report_id}")
async def publish_report(report_id: str, user=Depends(teacher_or_admin)):
    try:
        return snapshot_service.publish_report(report_id)
    except ReportNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SupabaseNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/reports/lock/{report_id}")
async def lock_report(report_id: str, user=Depends(teacher_or_admin)):
    try:
        return snapshot_service.lock_report(report_id)
    except ReportNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SupabaseNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/reports/preview")
def preview_report(student: StudentInput, use_ai: bool = False, user=Depends(teacher_or_admin)):
    """Returns the fully-calculated report as JSON for the teacher to
    review/edit before generating the final file, and persists a draft
    row so it can later be published/locked. Never raises a raw
    stack trace to the client."""
    try:
        engine = CalculationEngine()

        # 1. Calculate subject metrics
        subject_metrics = []
        subject_marks = student.subject_marks
        subject_max = student.subject_max_marks or {k: 100 for k in subject_marks}

        for sub, mark in subject_marks.items():
            metrics = engine.calculate_subject_metrics(mark, subject_max.get(sub, 100))
            subject_metrics.append({
                "subject": sub,
                **metrics
            })

        # 2. Calculate overall metrics
        overall = engine.calculate_overall_metrics([
            {"marks": m, "max_marks": mx}
            for sub, m in subject_marks.items()
            for mx in [subject_max.get(sub, 100)]
        ])

        # 3. Calculate attendance
        attendance = engine.calculate_attendance_metrics(
            student.present_days, student.working_days
        )

        report_data = {
            "student": {
                "name": student.name,
                "class": student.class_,
                "section": student.section,
                "roll": student.roll_number
            },
            "subjects": subject_metrics,
            "overall": overall,
            "attendance": attendance,
            "config": {
                "school_name": "AECS MAGNOLIA SCHOOL",
                "academic_year": student.academic_year
            }
        }

        # 4. Persist a draft row, if Supabase is configured, so the report
        # can be published/locked later. Preview still works without a DB.
        try:
            client = get_client()
            inserted = client.table("student_reports").insert({
                "student_name": student.name,
                "class": student.class_,
                "section": student.section,
                "roll_number": student.roll_number,
                "academic_year": student.academic_year,
                "input_payload": student.model_dump(by_alias=True),
                "report_payload": report_data,
                "status": "draft",
            }).execute()
            report_data["report_id"] = inserted.data[0]["id"]
        except SupabaseNotConfiguredError:
            report_data["report_id"] = None

        return report_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preview error: {str(e)}")


@router.post("/reports/generate/docx")
def generate_student_docx(student: StudentInput, observation_override: Optional[str] = Body(default=None), user=Depends(teacher_or_admin)):
    try:
        report_data = build_report(student)
        if observation_override:
            report_data["observation"] = observation_override
        file_bytes = generate_docx(report_data)
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong generating the Word document. Please try again.")

    filename = f"{_safe_filename(student.name)}.docx"
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/reports/generate/pdf")
def generate_student_pdf(student: StudentInput, observation_override: Optional[str] = Body(default=None), user=Depends(teacher_or_admin)):
    try:
        # 1. Calculate data using CalculationEngine (same as preview)
        engine = CalculationEngine()
        subject_metrics = []
        subject_marks = student.subject_marks
        subject_max = student.subject_max_marks or {k: 100 for k in subject_marks}
        for sub, mark in subject_marks.items():
            metrics = engine.calculate_subject_metrics(mark, subject_max.get(sub, 100))
            subject_metrics.append({"subject": sub, **metrics})

        overall = engine.calculate_overall_metrics([
            {"marks": m, "max_marks": mx}
            for sub, m in subject_marks.items()
            for mx in [subject_max.get(sub, 100)]
        ])

        attendance = engine.calculate_attendance_metrics(student.present_days, student.working_days)

        report_data = {
            "student": {"name": student.name, "class": student.class_, "section": student.section, "roll": student.roll_number},
            "subjects": subject_metrics,
            "overall": overall,
            "attendance": attendance,
            "observation": observation_override or "No remarks provided.",
            "config": {"school_name": "AECS MAGNOLIA SCHOOL", "academic_year": student.academic_year, "primary_color": "#1F4E8C"}
        }

        # 2. Generate PDF using PDFGenerator
        pdf_gen = PDFGenerator(report_data["config"])
        file_bytes = pdf_gen.generate(report_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation failed: {str(e)}")

    filename = f"{_safe_filename(student.name)}.pdf"
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/reports/inspect")
async def inspect_workbook(file: UploadFile = File(...), user=Depends(teacher_or_admin)):
    """
    Analyzes an uploaded workbook's structure.
    Used during Import Profile creation.
    """
    contents = await file.read()
    try:
        inspector = WorkbookInspector(contents)
        return inspector.inspect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workbook inspection failed: {str(e)}")

@router.post("/reports/upload")
async def upload_excel(file: UploadFile = File(...), user=Depends(teacher_or_admin)):
    """Validates an uploaded Excel file and returns valid students + any
    per-row issues, without generating files yet."""
    contents = await file.read()
    try:
        result = process_excel(contents)
    except ExcelValidationError as e:
        return JSONResponse(status_code=422, content={
            "error": e.message,
            "missing_columns": e.missing_columns,
        })
    return result


@router.get("/reports/template")
def download_template(user=Depends(teacher_or_admin)):
    file_bytes = build_template_bytes()
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="student_report_template.xlsx"'},
    )


@router.post("/reports/bulk/zip")
def generate_bulk_zip(students: List[StudentInput], user=Depends(teacher_or_admin)):
    try:
        config = {"school_name": "AECS MAGNOLIA SCHOOL", "academic_year": "2026-27", "primary_color": "#1F4E8C"}
        zip_bytes = bulk_service.generate_zip(students, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk ZIP generation failed: {str(e)}")

    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="student_reports.zip"'},
    )


def _build_pdf_report_data(student: StudentInput, config: dict, engine: CalculationEngine) -> dict:
    """Builds the report_data shape PDFGenerator expects (same shape used
    by /reports/generate/pdf), as distinct from build_report()'s shape,
    which is for the DOCX path."""
    subject_marks = student.subject_marks
    subject_max = student.subject_max_marks or {k: 100 for k in subject_marks}
    subject_metrics = [
        {"subject": sub, **engine.calculate_subject_metrics(mark, subject_max.get(sub, 100))}
        for sub, mark in subject_marks.items()
    ]
    overall = engine.calculate_overall_metrics([
        {"marks": m, "max_marks": subject_max.get(sub, 100)}
        for sub, m in subject_marks.items()
    ])
    attendance = engine.calculate_attendance_metrics(student.present_days, student.working_days)
    return {
        "student": {"name": student.name, "class": student.class_, "section": student.section, "roll": student.roll_number},
        "subjects": subject_metrics,
        "overall": overall,
        "attendance": attendance,
        "observation": student.teacher_remark or "No remarks provided.",
        "config": config,
    }


@router.post("/reports/bulk/combined-pdf")
def generate_bulk_combined_pdf(students: List[StudentInput], user=Depends(teacher_or_admin)):
    try:
        config = {"school_name": "AECS MAGNOLIA SCHOOL", "academic_year": "2026-27", "primary_color": "#1F4E8C"}
        engine = CalculationEngine()
        report_data_list = [_build_pdf_report_data(s, config, engine) for s in students]
        file_bytes = generate_combined_pdf(report_data_list)
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong generating the combined PDF. Please try again.")

    return StreamingResponse(
        io.BytesIO(file_bytes), media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="all_students_combined.pdf"'},
    )
