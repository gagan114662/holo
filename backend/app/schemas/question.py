"""
Question schemas for curriculum and grading
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

from ..models.question import QuestionType, DifficultyLevel


class QuestionCreate(BaseModel):
    subject_id: UUID
    skill_id: Optional[UUID] = None
    content: str = Field(..., min_length=10, max_length=10000)  # The question text/content
    question_type: QuestionType
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    options: Optional[list[str]] = Field(None, max_length=10)  # For multiple choice, max 10 options
    correct_answer: str = Field(..., min_length=1, max_length=5000)
    explanation: str = Field(..., min_length=1, max_length=10000)
    hints: Optional[list[str]] = Field(None, max_length=5)  # Max 5 hints
    extra_data: Optional[dict] = None  # Renamed from metadata

    class Config:
        use_enum_values = True


class QuestionResponse(BaseModel):
    id: UUID
    subject_id: UUID
    subject_name: Optional[str] = None
    skill_id: Optional[UUID] = None
    skill_name: Optional[str] = None
    content: str  # The question text/content
    question_type: QuestionType
    difficulty: DifficultyLevel
    options: Optional[list[str]] = None
    hints: Optional[list[str]] = None
    # Note: correct_answer is NOT exposed in response for security

    class Config:
        from_attributes = True
        use_enum_values = True


class AnswerSubmit(BaseModel):
    question_id: UUID
    answer: str = Field(..., min_length=1, max_length=10000)
    time_taken_seconds: Optional[int] = Field(None, ge=0, le=3600)  # Max 1 hour
    session_id: Optional[UUID] = None


class GradeResponse(BaseModel):
    is_correct: bool
    is_partial: bool = False
    score: float = Field(..., ge=0, le=1)  # 0.0 to 1.0
    feedback: str
    explanation: Optional[str] = None
    correct_answer: Optional[str] = None  # Only revealed after grading
    xp_earned: int = 0
    streak_bonus: int = 0
    mastery_change: Optional[float] = None


class QuestionFilter(BaseModel):
    subject_id: Optional[UUID] = None
    skill_id: Optional[UUID] = None
    difficulty: Optional[DifficultyLevel] = None
    question_type: Optional[QuestionType] = None
    exclude_mastered: bool = True
    use_spaced_repetition: bool = True


class NextQuestionRequest(BaseModel):
    subject_id: Optional[UUID] = None
    preferred_difficulty: Optional[DifficultyLevel] = None
    session_id: Optional[UUID] = None


class SubjectResponse(BaseModel):
    id: UUID
    name: str
    display_name: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    question_count: int = 0
    
    class Config:
        from_attributes = True


class SkillResponse(BaseModel):
    id: UUID
    subject_id: UUID
    name: str
    display_name: str
    description: Optional[str]
    prerequisites: Optional[list[UUID]] = None
    question_count: int = 0
    
    class Config:
        from_attributes = True
