"""
User schemas for authentication and user management
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.STUDENT
    grade_level: Optional[str] = None
    
    class Config:
        use_enum_values = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: UserRole
    grade_level: Optional[str]
    streak_days: int
    total_xp: int
    avatar_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    grade_level: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserPreferencesUpdate(BaseModel):
    preferred_subjects: Optional[list[str]] = Field(None, max_length=20)  # Max 20 subjects
    preferred_avatar: Optional[str] = Field(None, max_length=50)
    voice_enabled: Optional[bool] = None
    difficulty_preference: Optional[str] = Field(None, max_length=20)
    daily_goal_minutes: Optional[int] = Field(None, ge=5, le=480)  # 5 min to 8 hours
