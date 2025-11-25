"""
Question, Subject, and Skill models
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FREE_TEXT = "free_text"
    NUMERIC = "numeric"
    CODE = "code"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    MATCHING = "matching"


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    parent_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("Subject", remote_side=[id], backref="children")
    skills = relationship("Skill", back_populates="subject")


from sqlalchemy import Boolean


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    prerequisites = Column(ARRAY(UUID(as_uuid=True)), default=[])
    difficulty_level = Column(Integer, default=1)  # 1-5
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="skills")
    questions = relationship("Question", back_populates="skill")

    # Index for faster queries
    __table_args__ = (
        {"schema": None},
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)

    # Content
    content = Column(Text, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-5

    # Answer data
    correct_answer = Column(Text, nullable=True)
    options = Column(JSONB, nullable=True)  # For multiple choice: [{"id": "a", "text": "..."}]
    explanation = Column(Text, nullable=True)
    hints = Column(ARRAY(Text), default=[])

    # Grading
    rubric = Column(Text, nullable=True)  # For open-ended questions
    max_points = Column(Integer, default=100)
    partial_credit_allowed = Column(Boolean, default=True)

    # For code questions
    test_cases = Column(JSONB, nullable=True)  # [{"input": "...", "expected": "..."}]
    starter_code = Column(Text, nullable=True)
    language = Column(String(20), nullable=True)

    # Metadata
    tags = Column(ARRAY(String(50)), default=[])
    source = Column(String(100), nullable=True)  # "generated", "imported", "manual"
    metadata = Column(JSONB, default={})

    # Stats
    times_shown = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    avg_time_seconds = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_reviewed = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skill = relationship("Skill", back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question")

    @property
    def success_rate(self) -> float:
        if self.times_shown == 0:
            return 0.0
        return self.times_correct / self.times_shown

    def __repr__(self):
        return f"<Question {self.id} - {self.question_type}>"
