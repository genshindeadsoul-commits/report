from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
from app.utils.auth import teacher_or_admin
from app.services.staging_service import ImportStagingService
from app.services.workbook_inspector import WorkbookInspector
from app.services.commit_service import ImportCommitService

router = APIRouter()
staging_service = ImportStagingService()
commit_service = ImportCommitService(staging_service)

@router.post("/imports/stage")
async def stage_import(file: UploadFile = File(...), profile_id: str = None, user=Depends(teacher_or_admin)):
    """
    Uploads a workbook and stages the data for import.
    """
    contents = await file.read()

    # 1. Inspect workbook
    inspector = WorkbookInspector(contents)
    inspection = inspector.inspect()

    # 2. Mock: Convert the inspection/workbook to raw rows
    # In a real app, this would use the profile mappings to extract data
    mock_rows = [
        {"admission_number": "101", "full_name": "Student A", "marks": 85},
        {"admission_number": "102", "full_name": "Student B", "marks": "invalid"}, # Should cause error
    ]

    import_id = "mock-import-id"
    result = staging_service.stage_data(import_id, mock_rows)

    return {
        "import_id": import_id,
        **result
    }

@router.post("/imports/commit/{import_id}")
async def commit_import(import_id: str, user=Depends(admin_only)):
    try:
        return commit_service.commit_import(import_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/imports/reverse/{import_id}")
async def reverse_import(import_id: str, user=Depends(admin_only)):
    return commit_service.reverse_import(import_id)

@router.get("/imports/dry-run/{import_id}")
async def get_dry_run(import_id: str, user=Depends(teacher_or_admin)):
    report = staging_service.get_dry_run_report(import_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    return report
