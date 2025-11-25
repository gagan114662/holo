"""
User model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    PARENT = "parent"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

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
