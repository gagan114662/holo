"""
Progress tracking models
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("tutoring_sessions.id"), nullable=True, index=True)

    # Attempt data
    answer_given = Column(Text, nullable=False)  # Renamed from 'answer'
    is_correct = Column(Boolean, nullable=False)
    is_partial = Column(Boolean, default=False)  # Partial credit given
    score = Column(Integer, nullable=False)  # 0-100
    time_taken_seconds = Column(Integer, nullable=True)  # Renamed from 'time_spent_seconds'
    xp_earned = Column(Integer, default=0)  # XP awarded for this attempt

    # Feedback
    feedback = Column(Text, nullable=True)
    hints_used = Column(Integer, default=0)

    # Timestamps
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)  # Renamed from 'created_at'

    # Relationships
    user = relationship("User", back_populates="attempts")
    question = relationship("Question", back_populates="attempts")
    session = relationship("TutoringSession", back_populates="attempts")

    def __repr__(self):
        return f"<QuestionAttempt {self.id} - {'correct' if self.is_correct else 'incorrect'}>"


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Overall stats
    total_sessions = Column(Integer, default=0)
    total_attempted = Column(Integer, default=0)  # Renamed from 'total_questions_answered'
    total_correct = Column(Integer, default=0)  # Renamed from 'total_correct_answers'
    total_time_spent_minutes = Column(Integer, default=0)

    # Streaks
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)

    # Level/XP
    level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)

    # Achievements
    achievements = Column(JSONB, default=[])  # [{"id": "...", "unlocked_at": "..."}]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")
    skill_progress = relationship("SkillProgress", back_populates="user_progress")

    @property
    def accuracy(self) -> float:
        if self.total_attempted == 0:
            return 0.0
        return self.total_correct / self.total_attempted

    def __repr__(self):
        return f"<UserProgress user={self.user_id} level={self.level}>"


class SkillProgress(Base):
    __tablename__ = "skill_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_progress_id = Column(UUID(as_uuid=True), ForeignKey("user_progress.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)

    # Mastery
    mastery_level = Column(Float, default=0.0)  # 0.0 - 1.0
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)

    # Spaced repetition
    next_review_at = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5)  # For spaced repetition algorithm
    interval_days = Column(Integer, default=1)

    # Timestamps
    last_practiced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_progress = relationship("UserProgress", back_populates="skill_progress")
    skill = relationship("Skill")

    @property
    def accuracy(self) -> float:
        if self.questions_attempted == 0:
            return 0.0
        return self.questions_correct / self.questions_attempted

    def __repr__(self):
        return f"<SkillProgress skill={self.skill_id} mastery={self.mastery_level:.2f}>"
