"""
Progress Router
Handles student progress tracking and analytics
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..models.progress import UserProgress, SkillProgress, QuestionAttempt
from ..models.question import Subject, Skill
from ..schemas.progress import (
    ProgressResponse, SkillProgressResponse, SubjectProgressResponse,
    ActivityResponse, LeaderboardEntry, DailyGoalProgress
)
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=ProgressResponse)
async def get_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's overall progress"""
    # Get or create user progress
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user.id)
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = UserProgress(user_id=user.id)
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    
    # Calculate level from XP
    level = 1 + (user.total_xp // 1000)
    xp_to_next = 1000 - (user.total_xp % 1000)
    
    # Get subject progress
    subjects_progress = await _get_subject_progress(user.id, db)
    
    # Get recent activity
    recent_activity = await _get_recent_activity(user.id, db)
    
    accuracy = progress.total_correct / progress.total_attempted if progress.total_attempted > 0 else 0
    
    return ProgressResponse(
        user_id=user.id,
        total_questions_attempted=progress.total_attempted,
        total_correct=progress.total_correct,
        accuracy_rate=accuracy,
        current_streak=progress.current_streak,
        longest_streak=progress.longest_streak,
        total_xp=user.total_xp,
        level=level,
        xp_to_next_level=xp_to_next,
        subjects_progress=subjects_progress,
        recent_activity=recent_activity
    )


@router.get("/skills", response_model=list[SkillProgressResponse])
async def get_skill_progress(
    subject_id: Optional[UUID] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get progress for all skills"""
    # Use JOIN to fetch skill data in a single query (avoid N+1)
    query = (
        select(SkillProgress, Skill.display_name)
        .join(Skill, SkillProgress.skill_id == Skill.id)
        .where(SkillProgress.user_id == user.id)
    )

    if subject_id:
        query = query.where(SkillProgress.subject_id == subject_id)

    result = await db.execute(query)
    rows = result.all()

    responses = []
    for sp, skill_name in rows:
        responses.append(SkillProgressResponse(
            skill_id=sp.skill_id,
            skill_name=skill_name or "Unknown",
            subject_id=sp.subject_id,
            mastery_level=sp.mastery_level,
            questions_attempted=sp.questions_attempted,
            questions_correct=sp.questions_correct,
            last_practiced=sp.last_practiced_at,
            next_review=sp.next_review_at,
            streak=sp.current_streak
        ))

    return responses


@router.get("/daily", response_model=DailyGoalProgress)
async def get_daily_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get today's progress towards daily goal"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's attempts
    result = await db.execute(
        select(QuestionAttempt).where(
            and_(
                QuestionAttempt.user_id == user.id,
                QuestionAttempt.attempted_at >= today_start
            )
        )
    )
    today_attempts = result.scalars().all()
    
    questions_today = len(today_attempts)
    correct_today = sum(1 for a in today_attempts if a.is_correct)

    # Calculate actual time from attempts (fall back to estimate if no time data)
    total_time_seconds = sum(a.time_taken_seconds or 30 for a in today_attempts)
    completed_minutes = total_time_seconds // 60

    # Default daily goal (could be user-configurable in future)
    goal_minutes = 15

    # Check streak: user must have practiced today AND yesterday to maintain
    yesterday_start = today_start - timedelta(days=1)
    yesterday_result = await db.execute(
        select(func.count(QuestionAttempt.id)).where(
            and_(
                QuestionAttempt.user_id == user.id,
                QuestionAttempt.attempted_at >= yesterday_start,
                QuestionAttempt.attempted_at < today_start
            )
        )
    )
    practiced_yesterday = yesterday_result.scalar() > 0
    streak_maintained = questions_today > 0 and (practiced_yesterday or user.streak_days == 0)

    return DailyGoalProgress(
        goal_minutes=goal_minutes,
        completed_minutes=completed_minutes,
        questions_today=questions_today,
        correct_today=correct_today,
        is_goal_met=completed_minutes >= goal_minutes,
        streak_maintained=streak_maintained
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get the global leaderboard"""
    logger.info(f"Fetching leaderboard with limit {limit}")

    # Single query with LEFT JOIN to get users and their progress together
    from sqlalchemy.orm import aliased
    result = await db.execute(
        select(User, UserProgress)
        .outerjoin(UserProgress, User.id == UserProgress.user_id)
        .order_by(User.total_xp.desc())
        .limit(limit)
    )
    rows = result.all()

    entries = []
    for rank, (user, progress) in enumerate(rows, 1):
        accuracy = 0
        if progress and progress.total_attempted > 0:
            accuracy = progress.total_correct / progress.total_attempted

        entries.append(LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            total_xp=user.total_xp,
            streak_days=user.streak_days,
            accuracy_rate=accuracy
        ))

    return entries


async def _get_subject_progress(user_id: UUID, db: AsyncSession) -> list[SubjectProgressResponse]:
    """Get progress breakdown by subject (optimized with single aggregation query)"""
    # Single query to get all progress data with aggregation
    from sqlalchemy import case
    progress_query = await db.execute(
        select(
            Subject.id,
            Subject.display_name,
            func.sum(SkillProgress.questions_attempted).label('total_attempted'),
            func.sum(SkillProgress.questions_correct).label('total_correct'),
            func.avg(SkillProgress.mastery_level).label('avg_mastery'),
            func.sum(case((SkillProgress.mastery_level >= 0.8, 1), else_=0)).label('skills_mastered'),
            func.count(SkillProgress.id).label('skill_count')
        )
        .join(SkillProgress, and_(
            SkillProgress.subject_id == Subject.id,
            SkillProgress.user_id == user_id
        ))
        .where(Subject.is_active == True)
        .group_by(Subject.id, Subject.display_name)
    )
    progress_rows = progress_query.all()

    # Get total skills per subject in a single query
    total_skills_query = await db.execute(
        select(Skill.subject_id, func.count(Skill.id).label('total'))
        .where(Skill.is_active == True)
        .group_by(Skill.subject_id)
    )
    total_skills_map = {row.subject_id: row.total for row in total_skills_query.all()}

    progress_list = []
    for row in progress_rows:
        total_attempted = row.total_attempted or 0
        total_correct = row.total_correct or 0

        progress_list.append(SubjectProgressResponse(
            subject_id=row.id,
            subject_name=row.display_name,
            questions_attempted=total_attempted,
            questions_correct=total_correct,
            accuracy_rate=total_correct / total_attempted if total_attempted > 0 else 0,
            mastery_level=float(row.avg_mastery or 0),
            skills_mastered=int(row.skills_mastered or 0),
            total_skills=total_skills_map.get(row.id, 0)
        ))

    return progress_list


async def _get_recent_activity(user_id: UUID, db: AsyncSession, limit: int = 10) -> list[ActivityResponse]:
    """Get recent activity for a user"""
    result = await db.execute(
        select(QuestionAttempt).where(
            QuestionAttempt.user_id == user_id
        ).order_by(QuestionAttempt.attempted_at.desc()).limit(limit)
    )
    attempts = result.scalars().all()
    
    activities = []
    for attempt in attempts:
        activities.append(ActivityResponse(
            timestamp=attempt.attempted_at,
            activity_type="question_answered",
            description="Answered a question" + (" correctly" if attempt.is_correct else ""),
            xp_earned=attempt.xp_earned if hasattr(attempt, 'xp_earned') else 0
        ))
    
    return activities
