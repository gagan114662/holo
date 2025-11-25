"""
Session schemas for tutoring sessions
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime


class SessionCreate(BaseModel):
    subject_id: Optional[UUID] = None
    avatar_id: str = Field("einstein", min_length=1, max_length=50)
    session_type: Literal["practice", "review", "assessment"] = "practice"


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    subject_id: Optional[UUID]
    avatar_id: str
    session_type: str
    questions_attempted: int
    questions_correct: int
    xp_earned: int
    started_at: datetime
    ended_at: Optional[datetime]
    duration_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "user"  # user, assistant, system


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    question_id: Optional[UUID]
    was_correct: Optional[bool]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SessionStats(BaseModel):
    total_sessions: int
    total_questions: int
    total_correct: int
    accuracy_rate: float
    total_time_minutes: int
    average_session_length: float
    favorite_subject: Optional[str]
    strongest_skill: Optional[str]
    weakest_skill: Optional[str]
