"""
Tutoring session models
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class TutoringSession(Base):
    __tablename__ = "tutoring_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Session info
    avatar_id = Column(String(50), nullable=False)
    avatar_name = Column(String(100), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)

    # Stats
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")
    subject = relationship("Subject")
    messages = relationship("SessionMessage", back_populates="session", order_by="SessionMessage.created_at")
    attempts = relationship("QuestionAttempt", back_populates="session")

    @property
    def accuracy(self) -> float:
        if self.questions_answered == 0:
            return 0.0
        return self.correct_answers / self.questions_answered

    def __repr__(self):
        return f"<TutoringSession {self.id} - {self.status}>"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionMessage(Base):
    __tablename__ = "session_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("tutoring_sessions.id"), nullable=False)

    # Message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Optional metadata
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=True)
    was_correct = Column(Boolean, nullable=True)
    emotion = Column(String(20), nullable=True)
    extra_data = Column(JSONB, default={})  # Renamed from 'metadata' (SQLAlchemy reserved)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("TutoringSession", back_populates="messages")
    question = relationship("Question")

    def __repr__(self):
        return f"<SessionMessage {self.role} - {self.content[:50]}...>"
