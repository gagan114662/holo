"""
Classroom and enrollment models for teacher dashboard
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Class info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    grade_level = Column(String(20), nullable=True)  # "K", "1", "2", ..., "12", "college"

    # Settings
    join_code = Column(String(10), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    allow_self_enroll = Column(Boolean, default=True)
    max_students = Column(Integer, default=50)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("User", back_populates="taught_classes")
    subject = relationship("Subject")
    enrollments = relationship("Enrollment", back_populates="classroom")

    @property
    def student_count(self) -> int:
        return len([e for e in self.enrollments if e.is_active])

    def __repr__(self):
        return f"<Classroom {self.name}>"


class EnrollmentStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REMOVED = "removed"
    COMPLETED = "completed"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Status
    status = Column(SQLEnum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    is_active = Column(Boolean, default=True)

    # Progress in class
    assignments_completed = Column(Integer, default=0)
    total_score = Column(Integer, default=0)

    # Timestamps
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=True)

    # Relationships
    classroom = relationship("Classroom", back_populates="enrollments")
    student = relationship("User", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment student={self.student_id} class={self.classroom_id}>"
