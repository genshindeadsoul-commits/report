from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from app.utils.auth import admin_only, teacher_or_admin

router = APIRouter()

# Schemas
class StudentCreate(BaseModel):
    admission_number: str
    full_name: str
    date_of_birth: str
    email: str = None
    phone_number: str = None

class EnrollmentCreate(BaseModel):
    student_id: str
    academic_year_id: str
    class_id: str
    section_id: str
    roll_number: str

# Mock Data Store
DATA = {
    "students": [],
    "enrollments": []
}

@router.get("/students")
async def get_students(user=Depends(teacher_or_admin)):
    return DATA["students"]

@router.post("/students", dependencies=[Depends(admin_only)])
async def create_student(student: StudentCreate):
    DATA["students"].append(student.dict())
    return {"status": "created"}

@router.get("/enrollments")
async def get_enrollments(user=Depends(teacher_or_admin)):
    return DATA["enrollments"]

@router.post("/enrollments", dependencies=[Depends(admin_only)])
async def create_enrollment(enrollment: EnrollmentCreate):
    DATA["enrollments"].append(enrollment.dict())
    return {"status": "created"}
