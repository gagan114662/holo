"""
User model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base
from .utils import GUID


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    PARENT = "parent"


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Null if using Firebase auth only
    display_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    grade_level = Column(String(20), nullable=True)  # e.g., "6th", "7th", "high_school"
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Progress tracking
    total_xp = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)

    # Preferences
    preferred_language = Column(String(10), default="en")
    preferred_avatar_id = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    attempts = relationship("QuestionAttempt", back_populates="user")
    sessions = relationship("TutoringSession", back_populates="user")
    enrollments = relationship("Enrollment", back_populates="student")
    taught_classes = relationship("Classroom", back_populates="teacher")

    def __repr__(self):
        return f"<User {self.email}>"
