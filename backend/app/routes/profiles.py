from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any
from pydantic import BaseModel
from app.utils.auth import admin_only, teacher_or_admin
from app.services.workbook_inspector import WorkbookInspector
from app.services.profile_matcher import ProfileMatcher

router = APIRouter()

# Schemas
class ProfileCreate(BaseModel):
    name: str
    description: str = ""
    academic_year_id: str
    signature: Dict[str, Any]
    mappings: Dict[str, Any]

class ProfileTestRequest(BaseModel):
    profile_id: str
    workbook_bytes: bytes

@router.get("/profiles")
async def list_profiles(user=Depends(teacher_or_admin)):
    # In a real app: query the 'import_profiles' table
    return []

@router.post("/profiles", dependencies=[Depends(admin_only)])
async def create_profile(profile: ProfileCreate):
    # In a real app: insert into 'import_profiles' table
    return {"status": "created", "id": "mock-profile-id"}

@router.post("/profiles/match")
async def match_profile(profile_id: str, file: UploadFile = File(...), user=Depends(teacher_or_admin)):
    """
    Matches an uploaded workbook against a specific profile.
    """
    contents = await file.read()
    inspector = WorkbookInspector(contents)
    inspection = inspector.inspect()

    # In a real app: Load profile from DB using profile_id
    mock_profile = {
        "name": "Test Profile",
        "expected_sheet": "Students",
        "mappings": {"Admission Number": "0", "Student Name": "1", "Class": "2"}
    }

    matcher = ProfileMatcher(mock_profile, inspection)
    return matcher.calculate_match()

@router.post("/profiles/test")
async def test_profile(profile_id: str, file: UploadFile = File(...), user=Depends(teacher_or_admin)):
    """
    Tests a profile against a workbook and returns a compatibility report.
    """
    contents = await file.read()
    inspector = WorkbookInspector(contents)
    inspection = inspector.inspect()

    # Mock compatibility check logic
    # In reality, we would load the profile from DB and compare signatures
    return {
        "compatibility_score": 0.95,
        "matched_fields": ["Admission Number", "Student Name", "Class"],
        "missing_fields": ["Attendance"],
        "warnings": ["Some subject headers are slightly different"]
    }
