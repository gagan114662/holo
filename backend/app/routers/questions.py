"""
Questions Router
Handles question fetching, answer submission, and grading
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import random

from ..database import get_db
from ..models.user import User
from ..models.question import Question, Subject, Skill, DifficultyLevel
from ..models.progress import QuestionAttempt, SkillProgress, UserProgress
from ..schemas.question import (
    QuestionResponse, AnswerSubmit, GradeResponse,
    NextQuestionRequest, SubjectResponse, SkillResponse
)
from .auth import get_current_user
from ..services.grading import GradingService

logger = logging.getLogger(__name__)

router = APIRouter()
grading_service = GradingService()


@router.get("/subjects", response_model=list[SubjectResponse])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    """Get all available subjects"""
    result = await db.execute(
        select(Subject).where(Subject.is_active == True).order_by(Subject.display_name)
    )
    subjects = result.scalars().all()
    
    # Add question counts
    responses = []
    for subject in subjects:
        count_result = await db.execute(
            select(func.count(Question.id)).where(
                and_(Question.subject_id == subject.id, Question.is_active == True)
            )
        )
        count = count_result.scalar() or 0
        resp = SubjectResponse.model_validate(subject)
        resp.question_count = count
        responses.append(resp)
    
    return responses


@router.get("/subjects/{subject_id}/skills", response_model=list[SkillResponse])
async def get_skills(subject_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all skills for a subject"""
    result = await db.execute(
        select(Skill).where(
            and_(Skill.subject_id == subject_id, Skill.is_active == True)
        ).order_by(Skill.order_index)
    )
    skills = result.scalars().all()
    
    responses = []
    for skill in skills:
        count_result = await db.execute(
            select(func.count(Question.id)).where(
                and_(Question.skill_id == skill.id, Question.is_active == True)
            )
        )
        count = count_result.scalar() or 0
        resp = SkillResponse.model_validate(skill)
        resp.question_count = count
        responses.append(resp)
    
    return responses


@router.get("/next", response_model=QuestionResponse)
async def get_next_question(
    subject_id: Optional[UUID] = None,
    skill_id: Optional[UUID] = None,
    difficulty: Optional[DifficultyLevel] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the next question using spaced repetition algorithm"""
    
    # Build base query
    query = select(Question).where(Question.is_active == True)
    
    if subject_id:
        query = query.where(Question.subject_id == subject_id)
    if skill_id:
        query = query.where(Question.skill_id == skill_id)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    
    # Get user's skill progress for spaced repetition
    skills_due = await db.execute(
        select(SkillProgress).where(
            and_(
                SkillProgress.user_id == user.id,
                or_(
                    SkillProgress.next_review_at <= datetime.utcnow(),
                    SkillProgress.next_review_at == None
                )
            )
        )
    )
    due_skill_ids = [sp.skill_id for sp in skills_due.scalars().all()]
    
    # Prioritize skills due for review
    if due_skill_ids:
        query = query.where(Question.skill_id.in_(due_skill_ids))
    
    # Get recently answered questions to avoid repetition
    recent_attempts = await db.execute(
        select(QuestionAttempt.question_id).where(
            and_(
                QuestionAttempt.user_id == user.id,
                QuestionAttempt.attempted_at >= datetime.utcnow() - timedelta(hours=24)
            )
        ).distinct()
    )
    recent_question_ids = [a for a in recent_attempts.scalars().all()]
    
    if recent_question_ids:
        query = query.where(Question.id.notin_(recent_question_ids))
    
    # Execute query
    result = await db.execute(query.order_by(func.random()).limit(10))
    questions = result.scalars().all()
    
    if not questions:
        # If no questions found with filters, try without exclusions
        fallback_query = select(Question).where(Question.is_active == True)
        if subject_id:
            fallback_query = fallback_query.where(Question.subject_id == subject_id)
        result = await db.execute(fallback_query.order_by(func.random()).limit(1))
        questions = result.scalars().all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions available")
    
    # Select one question, preferring lower mastery skills
    question = random.choice(questions)
    
    # Get subject and skill names
    subject_result = await db.execute(select(Subject).where(Subject.id == question.subject_id))
    subject = subject_result.scalar_one_or_none()
    
    skill_result = None
    if question.skill_id:
        skill_result = await db.execute(select(Skill).where(Skill.id == question.skill_id))
        skill = skill_result.scalar_one_or_none()
    
    response = QuestionResponse.model_validate(question)
    response.subject_name = subject.display_name if subject else None
    response.skill_name = skill.display_name if skill_result and skill else None
    
    return response


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific question by ID"""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionResponse.model_validate(question)


@router.post("/submit", response_model=GradeResponse)
async def submit_answer(
    submission: AnswerSubmit,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit an answer for grading"""
    # Get the question
    result = await db.execute(select(Question).where(Question.id == submission.question_id))
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Grade the answer using the grading service
    grade_result = await grading_service.grade_answer(
        question=question,
        student_answer=submission.answer,
        db=db
    )
    
    # Calculate XP
    base_xp = {
        DifficultyLevel.EASY: 10,
        DifficultyLevel.MEDIUM: 20,
        DifficultyLevel.HARD: 35,
        DifficultyLevel.EXPERT: 50
    }.get(question.difficulty, 15)
    
    xp_earned = int(base_xp * grade_result["score"]) if grade_result["is_correct"] else 0
    streak_bonus = 0
    
    # Get user progress for streak
    progress_result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user.id)
    )
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        progress = UserProgress(user_id=user.id)
        db.add(progress)
    
    # Update streak
    if grade_result["is_correct"]:
        progress.current_streak += 1
        if progress.current_streak > progress.longest_streak:
            progress.longest_streak = progress.current_streak
        
        # Streak bonus: +5% per correct answer in streak, max 50%
        streak_bonus = min(int(xp_earned * 0.05 * progress.current_streak), int(xp_earned * 0.5))
        xp_earned += streak_bonus
        progress.total_correct += 1
    else:
        progress.current_streak = 0
    
    progress.total_attempted += 1
    progress.last_activity_at = datetime.utcnow()
    
    # Update user XP
    user.total_xp += xp_earned
    
    # Record the attempt
    attempt = QuestionAttempt(
        user_id=user.id,
        question_id=question.id,
        session_id=submission.session_id,
        answer_given=submission.answer,
        is_correct=grade_result["is_correct"],
        is_partial=grade_result.get("is_partial", False),
        score=grade_result["score"],
        time_taken_seconds=submission.time_taken_seconds,
        feedback=grade_result["feedback"]
    )
    db.add(attempt)
    
    # Update skill progress for spaced repetition
    if question.skill_id:
        skill_progress_result = await db.execute(
            select(SkillProgress).where(
                and_(
                    SkillProgress.user_id == user.id,
                    SkillProgress.skill_id == question.skill_id
                )
            )
        )
        skill_progress = skill_progress_result.scalar_one_or_none()
        
        if not skill_progress:
            skill_progress = SkillProgress(
                user_id=user.id,
                skill_id=question.skill_id,
                subject_id=question.subject_id
            )
            db.add(skill_progress)
        
        # Update spaced repetition parameters
        skill_progress.questions_attempted += 1
        if grade_result["is_correct"]:
            skill_progress.questions_correct += 1
            skill_progress.current_streak += 1
            
            # SM-2 algorithm for spaced repetition
            if skill_progress.current_streak >= 3:
                skill_progress.ease_factor = max(1.3, skill_progress.ease_factor + 0.1)
                skill_progress.interval_days = int(skill_progress.interval_days * skill_progress.ease_factor)
            
            skill_progress.mastery_level = min(1.0, skill_progress.mastery_level + 0.05)
        else:
            skill_progress.current_streak = 0
            skill_progress.ease_factor = max(1.3, skill_progress.ease_factor - 0.2)
            skill_progress.interval_days = 1
            skill_progress.mastery_level = max(0.0, skill_progress.mastery_level - 0.02)
        
        skill_progress.next_review_at = datetime.utcnow() + timedelta(days=skill_progress.interval_days)
        skill_progress.last_practiced_at = datetime.utcnow()
    
    await db.commit()
    
    return GradeResponse(
        is_correct=grade_result["is_correct"],
        is_partial=grade_result.get("is_partial", False),
        score=grade_result["score"],
        feedback=grade_result["feedback"],
        explanation=question.explanation if not grade_result["is_correct"] else None,
        correct_answer=question.correct_answer if not grade_result["is_correct"] else None,
        xp_earned=xp_earned,
        streak_bonus=streak_bonus,
        mastery_change=0.05 if grade_result["is_correct"] else -0.02
    )


# ACE Adaptive Tutoring Endpoints

@router.post("/{question_id}/hint")
async def get_hint(
    question_id: UUID,
    student_attempt: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get an adaptive hint for a question using ACE"""
    from ..services.ace_tutoring import ace_tutor

    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get subject name for context
    subject_name = "general"
    if question.subject_id:
        subject_result = await db.execute(select(Subject).where(Subject.id == question.subject_id))
        subject = subject_result.scalar_one_or_none()
        if subject:
            subject_name = subject.display_name

    hint = await ace_tutor.get_hint(
        question_content=question.content,
        correct_answer=question.correct_answer,
        student_attempt=student_attempt,
        subject=subject_name,
        grade_level=user.grade_level or 8,
    )

    return {"hint": hint}


@router.post("/{question_id}/explain")
async def explain_concept(
    question_id: UUID,
    student_question: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get an explanation for a concept related to a question"""
    from ..services.ace_tutoring import ace_tutor

    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get skill/topic name
    topic = "this concept"
    if question.skill_id:
        skill_result = await db.execute(select(Skill).where(Skill.id == question.skill_id))
        skill = skill_result.scalar_one_or_none()
        if skill:
            topic = skill.display_name

    explanation = await ace_tutor.explain_concept(
        topic=topic,
        question_context=question.content,
        student_question=student_question,
        grade_level=user.grade_level or 8,
    )

    return {"explanation": explanation}


@router.get("/tutor/difficulty-recommendation")
async def get_difficulty_recommendation(
    subject_id: Optional[UUID] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered difficulty recommendation based on recent performance"""
    from ..services.ace_tutoring import ace_tutor

    # Get recent attempts
    query = select(QuestionAttempt).where(
        QuestionAttempt.user_id == user.id
    ).order_by(QuestionAttempt.attempted_at.desc()).limit(20)

    result = await db.execute(query)
    attempts = result.scalars().all()

    if not attempts:
        return {
            "recommendation": "maintain",
            "reason": "Not enough data yet",
            "confidence": 0.3,
            "suggested_difficulty": "MEDIUM"
        }

    # Calculate recent accuracy
    correct = sum(1 for a in attempts if a.is_correct)
    accuracy = correct / len(attempts)

    # Get current difficulty from most common recent difficulty
    # For now, assume MEDIUM as baseline
    current_difficulty = "MEDIUM"

    recommendation = await ace_tutor.adapt_difficulty_recommendation(
        recent_accuracy=accuracy,
        current_difficulty=current_difficulty,
        questions_attempted=len(attempts),
    )

    # Map recommendation to difficulty level
    difficulty_map = {
        "EASY": {"increase": "MEDIUM", "decrease": "EASY", "maintain": "EASY"},
        "MEDIUM": {"increase": "HARD", "decrease": "EASY", "maintain": "MEDIUM"},
        "HARD": {"increase": "HARD", "decrease": "MEDIUM", "maintain": "HARD"},
    }

    suggested = difficulty_map.get(current_difficulty, {}).get(
        recommendation.get("recommendation", "maintain"),
        "MEDIUM"
    )

    return {
        **recommendation,
        "current_accuracy": accuracy,
        "attempts_analyzed": len(attempts),
        "suggested_difficulty": suggested
    }
