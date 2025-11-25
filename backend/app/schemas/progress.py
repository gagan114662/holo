"""
Progress schemas for tracking student advancement
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProgressResponse(BaseModel):
    user_id: UUID
    total_questions_attempted: int
    total_correct: int
    accuracy_rate: float
    current_streak: int
    longest_streak: int
    total_xp: int
    level: int
    xp_to_next_level: int
    subjects_progress: list["SubjectProgressResponse"]
    recent_activity: list["ActivityResponse"]
    
    class Config:
        from_attributes = True


class SubjectProgressResponse(BaseModel):
    subject_id: UUID
    subject_name: str
    questions_attempted: int
    questions_correct: int
    accuracy_rate: float
    mastery_level: float  # 0.0 to 1.0
    skills_mastered: int
    total_skills: int
    
    class Config:
        from_attributes = True


class SkillProgressResponse(BaseModel):
    skill_id: UUID
    skill_name: str
    subject_id: UUID
    mastery_level: float
    questions_attempted: int
    questions_correct: int
    last_practiced: Optional[datetime]
    next_review: Optional[datetime]
    streak: int
    
    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    timestamp: datetime
    activity_type: str  # question_answered, skill_mastered, level_up, streak
    description: str
    xp_earned: int = 0
    subject_name: Optional[str] = None


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    display_name: str
    avatar_url: Optional[str]
    total_xp: int
    streak_days: int
    accuracy_rate: float


class DailyGoalProgress(BaseModel):
    goal_minutes: int
    completed_minutes: int
    questions_today: int
    correct_today: int
    is_goal_met: bool
    streak_maintained: bool
