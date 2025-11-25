"""
Classroom schemas for teacher dashboard
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ClassroomCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    subject_id: Optional[UUID] = None
    grade_level: Optional[str] = None
    max_students: int = Field(default=50, ge=1, le=500)
    allow_self_enroll: bool = True


class ClassroomResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    name: str
    description: Optional[str]
    subject_id: Optional[UUID]
    subject_name: Optional[str] = None
    grade_level: Optional[str]
    join_code: str
    is_active: bool
    allow_self_enroll: bool
    max_students: int
    student_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    is_active: Optional[bool] = None
    allow_self_enroll: Optional[bool] = None
    max_students: Optional[int] = None


class EnrollmentResponse(BaseModel):
    id: UUID
    classroom_id: UUID
    student_id: UUID
    student_name: str
    student_email: str
    status: str
    is_active: bool
    assignments_completed: int
    total_score: int
    enrolled_at: datetime
    last_activity_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StudentProgress(BaseModel):
    student_id: UUID
    student_name: str
    avatar_url: Optional[str]
    questions_attempted: int
    questions_correct: int
    accuracy_rate: float
    time_spent_minutes: int
    last_active: Optional[datetime]
    streak_days: int
    mastery_levels: dict[str, float]  # skill_name -> mastery level


class ClassroomStats(BaseModel):
    classroom_id: UUID
    total_students: int
    active_students_today: int
    average_accuracy: float
    average_questions_per_student: float
    total_questions_answered: int
    top_performers: list[StudentProgress]
    struggling_students: list[StudentProgress]
    skill_breakdown: dict[str, float]  # skill_name -> average mastery


class JoinClassroom(BaseModel):
    join_code: str = Field(..., min_length=6, max_length=10)
