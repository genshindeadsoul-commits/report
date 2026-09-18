from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from app.utils.auth import admin_only

router = APIRouter()

# Schemas
class AcademicYearCreate(BaseModel):
    name: str
    start_date: str
    end_date: str
    status: str = "active"

class ClassCreate(BaseModel):
    name: str
    display_order: int = 0

class SectionCreate(BaseModel):
    class_id: str
    academic_year_id: str
    name: str

class SubjectCreate(BaseModel):
    code: str
    name: str
    display_order: int = 0

# Mock Data Store (to be replaced by Supabase calls in final implementation)
# In a real app, these would be async DB calls.
DATA = {
    "years": [],
    "classes": [],
    "sections": [],
    "subjects": []
}

@router.get("/config/years")
async def get_years():
    return DATA["years"]

@router.post("/config/years", dependencies=[Depends(admin_only)])
async def create_year(year: AcademicYearCreate):
    DATA["years"].append(year.dict())
    return {"status": "created"}

@router.get("/config/classes")
async def get_classes():
    return DATA["classes"]

@router.post("/config/classes", dependencies=[Depends(admin_only)])
async def create_class(cls: ClassCreate):
    DATA["classes"].append(cls.dict())
    return {"status": "created"}

@router.get("/config/sections")
async def get_sections():
    return DATA["sections"]

@router.post("/config/sections", dependencies=[Depends(admin_only)])
async def create_section(sec: SectionCreate):
    DATA["sections"].append(sec.dict())
    return {"status": "created"}

@router.get("/config/subjects")
async def get_subjects():
    return DATA["subjects"]

@router.post("/config/subjects", dependencies=[Depends(admin_only)])
async def create_subject(sub: SubjectCreate):
    DATA["subjects"].append(sub.dict())
    return {"status": "created"}
