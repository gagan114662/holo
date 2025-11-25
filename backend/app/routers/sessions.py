"""
Sessions Router
Handles tutoring session management
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.session import TutoringSession, SessionMessage
from ..models.question import Subject
from ..schemas.session import SessionCreate, SessionResponse, MessageCreate, MessageResponse, SessionStats
from .auth import get_current_user

router = APIRouter()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tutoring session"""
    session = TutoringSession(
        user_id=user.id,
        subject_id=session_data.subject_id,
        avatar_id=session_data.avatar_id,
        session_type=session_data.session_type,
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return SessionResponse.model_validate(session)


@router.get("/current", response_model=Optional[SessionResponse])
async def get_current_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's current active session"""
    result = await db.execute(
        select(TutoringSession).where(
            and_(
                TutoringSession.user_id == user.id,
                TutoringSession.ended_at == None
            )
        ).order_by(TutoringSession.started_at.desc())
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return None
    
    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session"""
    result = await db.execute(
        select(TutoringSession).where(
            and_(
                TutoringSession.id == session_id,
                TutoringSession.user_id == user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse.model_validate(session)


@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """End a tutoring session"""
    result = await db.execute(
        select(TutoringSession).where(
            and_(
                TutoringSession.id == session_id,
                TutoringSession.user_id == user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.ended_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)
    
    return SessionResponse.model_validate(session)


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def add_message(
    session_id: UUID,
    message_data: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a message to a session"""
    # Verify session ownership
    result = await db.execute(
        select(TutoringSession).where(
            and_(
                TutoringSession.id == session_id,
                TutoringSession.user_id == user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message = SessionMessage(
        session_id=session_id,
        role=message_data.message_type,
        content=message_data.content,
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return MessageResponse.model_validate(message)


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a session"""
    # Verify session ownership
    result = await db.execute(
        select(TutoringSession).where(
            and_(
                TutoringSession.id == session_id,
                TutoringSession.user_id == user.id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages_result = await db.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == session_id
        ).order_by(SessionMessage.timestamp)
    )
    messages = messages_result.scalars().all()
    
    return [MessageResponse.model_validate(m) for m in messages]


@router.get("/stats/summary", response_model=SessionStats)
async def get_session_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's session statistics"""
    # Total sessions
    total_sessions = await db.execute(
        select(func.count(TutoringSession.id)).where(TutoringSession.user_id == user.id)
    )
    
    # Total questions and correct
    total_questions = await db.execute(
        select(func.sum(TutoringSession.questions_attempted)).where(TutoringSession.user_id == user.id)
    )
    total_correct = await db.execute(
        select(func.sum(TutoringSession.questions_correct)).where(TutoringSession.user_id == user.id)
    )
    
    questions = total_questions.scalar() or 0
    correct = total_correct.scalar() or 0
    
    return SessionStats(
        total_sessions=total_sessions.scalar() or 0,
        total_questions=questions,
        total_correct=correct,
        accuracy_rate=correct / questions if questions > 0 else 0,
        total_time_minutes=0,  # TODO: Calculate from session durations
        average_session_length=0,
        favorite_subject=None,
        strongest_skill=None,
        weakest_skill=None
    )


@router.websocket("/ws/{session_id}")
async def websocket_session(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time session updates"""
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "message":
                # Broadcast to session
                await manager.send_message(session_id, data)
    except WebSocketDisconnect:
        manager.disconnect(session_id)
