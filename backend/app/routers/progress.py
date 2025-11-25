"""
Progress Router
Handles student progress tracking and analytics
"""
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
    query = select(SkillProgress).where(SkillProgress.user_id == user.id)
    
    if subject_id:
        query = query.where(SkillProgress.subject_id == subject_id)
    
    result = await db.execute(query)
    skill_progress_list = result.scalars().all()
    
    responses = []
    for sp in skill_progress_list:
        # Get skill name
        skill_result = await db.execute(select(Skill).where(Skill.id == sp.skill_id))
        skill = skill_result.scalar_one_or_none()
        
        responses.append(SkillProgressResponse(
            skill_id=sp.skill_id,
            skill_name=skill.display_name if skill else "Unknown",
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
    
    # Estimate time (assume ~30 seconds per question)
    completed_minutes = questions_today // 2
    
    # Get user's daily goal (default 15 minutes)
    goal_minutes = 15  # TODO: Get from user preferences
    
    return DailyGoalProgress(
        goal_minutes=goal_minutes,
        completed_minutes=completed_minutes,
        questions_today=questions_today,
        correct_today=correct_today,
        is_goal_met=completed_minutes >= goal_minutes,
        streak_maintained=questions_today > 0
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get the global leaderboard"""
    result = await db.execute(
        select(User).order_by(User.total_xp.desc()).limit(limit)
    )
    users = result.scalars().all()
    
    # Get progress for each user to calculate accuracy
    entries = []
    for rank, u in enumerate(users, 1):
        progress_result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == u.id)
        )
        progress = progress_result.scalar_one_or_none()
        
        accuracy = 0
        if progress and progress.total_attempted > 0:
            accuracy = progress.total_correct / progress.total_attempted
        
        entries.append(LeaderboardEntry(
            rank=rank,
            user_id=u.id,
            display_name=u.display_name,
            avatar_url=u.avatar_url,
            total_xp=u.total_xp,
            streak_days=u.streak_days,
            accuracy_rate=accuracy
        ))
    
    return entries


async def _get_subject_progress(user_id: UUID, db: AsyncSession) -> list[SubjectProgressResponse]:
    """Get progress breakdown by subject"""
    # Get all subjects
    subjects_result = await db.execute(select(Subject).where(Subject.is_active == True))
    subjects = subjects_result.scalars().all()
    
    progress_list = []
    for subject in subjects:
        # Get skill progress for this subject
        skill_progress_result = await db.execute(
            select(SkillProgress).where(
                and_(
                    SkillProgress.user_id == user_id,
                    SkillProgress.subject_id == subject.id
                )
            )
        )
        skill_progress = skill_progress_result.scalars().all()
        
        if not skill_progress:
            continue
        
        total_attempted = sum(sp.questions_attempted for sp in skill_progress)
        total_correct = sum(sp.questions_correct for sp in skill_progress)
        avg_mastery = sum(sp.mastery_level for sp in skill_progress) / len(skill_progress) if skill_progress else 0
        skills_mastered = sum(1 for sp in skill_progress if sp.mastery_level >= 0.8)
        
        # Count total skills for subject
        total_skills_result = await db.execute(
            select(func.count(Skill.id)).where(Skill.subject_id == subject.id)
        )
        total_skills = total_skills_result.scalar() or 0
        
        progress_list.append(SubjectProgressResponse(
            subject_id=subject.id,
            subject_name=subject.display_name,
            questions_attempted=total_attempted,
            questions_correct=total_correct,
            accuracy_rate=total_correct / total_attempted if total_attempted > 0 else 0,
            mastery_level=avg_mastery,
            skills_mastered=skills_mastered,
            total_skills=total_skills
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
