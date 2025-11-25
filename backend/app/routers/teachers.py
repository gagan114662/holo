"""
Teachers Router
Handles teacher dashboard and classroom management
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import secrets
import string

from ..database import get_db
from ..models.user import User, UserRole
from ..models.classroom import Classroom, Enrollment, EnrollmentStatus
from ..models.progress import QuestionAttempt, SkillProgress
from ..models.question import Subject, Skill
from ..schemas.classroom import (
    ClassroomCreate, ClassroomResponse, ClassroomUpdate,
    EnrollmentResponse, StudentProgress, ClassroomStats, JoinClassroom
)
from .auth import get_current_user, require_teacher

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_join_code() -> str:
    """Generate a unique 8-character join code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


@router.post("/classrooms", response_model=ClassroomResponse)
async def create_classroom(
    data: ClassroomCreate,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Create a new classroom"""
    # Generate unique join code
    join_code = generate_join_code()
    while True:
        existing = await db.execute(
            select(Classroom).where(Classroom.join_code == join_code)
        )
        if not existing.scalar_one_or_none():
            break
        join_code = generate_join_code()
    
    classroom = Classroom(
        teacher_id=user.id,
        name=data.name,
        description=data.description,
        subject_id=data.subject_id,
        grade_level=data.grade_level,
        join_code=join_code,
        max_students=data.max_students,
        allow_self_enroll=data.allow_self_enroll,
    )
    
    db.add(classroom)
    await db.commit()
    await db.refresh(classroom)
    
    # Get subject name if set
    subject_name = None
    if classroom.subject_id:
        subject_result = await db.execute(
            select(Subject).where(Subject.id == classroom.subject_id)
        )
        subject = subject_result.scalar_one_or_none()
        subject_name = subject.display_name if subject else None
    
    response = ClassroomResponse.model_validate(classroom)
    response.subject_name = subject_name
    response.student_count = 0
    
    return response


@router.get("/classrooms", response_model=list[ClassroomResponse])
async def get_classrooms(
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Get all classrooms for a teacher"""
    result = await db.execute(
        select(Classroom).where(
            Classroom.teacher_id == user.id
        ).order_by(Classroom.created_at.desc())
    )
    classrooms = result.scalars().all()
    
    responses = []
    for classroom in classrooms:
        # Count students
        count_result = await db.execute(
            select(func.count(Enrollment.id)).where(
                and_(
                    Enrollment.classroom_id == classroom.id,
                    Enrollment.is_active == True
                )
            )
        )
        student_count = count_result.scalar() or 0
        
        # Get subject name
        subject_name = None
        if classroom.subject_id:
            subject_result = await db.execute(
                select(Subject).where(Subject.id == classroom.subject_id)
            )
            subject = subject_result.scalar_one_or_none()
            subject_name = subject.display_name if subject else None
        
        response = ClassroomResponse.model_validate(classroom)
        response.student_count = student_count
        response.subject_name = subject_name
        responses.append(response)
    
    return responses


@router.get("/classrooms/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(
    classroom_id: UUID,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific classroom"""
    result = await db.execute(
        select(Classroom).where(
            and_(
                Classroom.id == classroom_id,
                Classroom.teacher_id == user.id
            )
        )
    )
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    return ClassroomResponse.model_validate(classroom)


@router.patch("/classrooms/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: UUID,
    updates: ClassroomUpdate,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Update a classroom"""
    result = await db.execute(
        select(Classroom).where(
            and_(
                Classroom.id == classroom_id,
                Classroom.teacher_id == user.id
            )
        )
    )
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    if updates.name is not None:
        classroom.name = updates.name
    if updates.description is not None:
        classroom.description = updates.description
    if updates.grade_level is not None:
        classroom.grade_level = updates.grade_level
    if updates.is_active is not None:
        classroom.is_active = updates.is_active
    if updates.allow_self_enroll is not None:
        classroom.allow_self_enroll = updates.allow_self_enroll
    if updates.max_students is not None:
        classroom.max_students = updates.max_students
    
    await db.commit()
    await db.refresh(classroom)
    
    return ClassroomResponse.model_validate(classroom)


@router.delete("/classrooms/{classroom_id}")
async def delete_classroom(
    classroom_id: UUID,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Delete a classroom"""
    result = await db.execute(
        select(Classroom).where(
            and_(
                Classroom.id == classroom_id,
                Classroom.teacher_id == user.id
            )
        )
    )
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    await db.delete(classroom)
    await db.commit()
    
    return {"message": "Classroom deleted"}


@router.get("/classrooms/{classroom_id}/students", response_model=list[EnrollmentResponse])
async def get_classroom_students(
    classroom_id: UUID,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Get all students in a classroom"""
    # Verify classroom ownership
    classroom_result = await db.execute(
        select(Classroom).where(
            and_(
                Classroom.id == classroom_id,
                Classroom.teacher_id == user.id
            )
        )
    )
    if not classroom_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get enrollments with student info
    result = await db.execute(
        select(Enrollment).where(Enrollment.classroom_id == classroom_id)
    )
    enrollments = result.scalars().all()
    
    responses = []
    for enrollment in enrollments:
        # Get student info
        student_result = await db.execute(
            select(User).where(User.id == enrollment.student_id)
        )
        student = student_result.scalar_one_or_none()
        
        if student:
            responses.append(EnrollmentResponse(
                id=enrollment.id,
                classroom_id=enrollment.classroom_id,
                student_id=enrollment.student_id,
                student_name=student.display_name,
                student_email=student.email,
                status=enrollment.status.value,
                is_active=enrollment.is_active,
                assignments_completed=enrollment.assignments_completed,
                total_score=enrollment.total_score,
                enrolled_at=enrollment.enrolled_at,
                last_activity_at=enrollment.last_activity_at
            ))
    
    return responses


@router.get("/classrooms/{classroom_id}/stats", response_model=ClassroomStats)
async def get_classroom_stats(
    classroom_id: UUID,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a classroom"""
    # Verify classroom ownership
    classroom_result = await db.execute(
        select(Classroom).where(
            and_(
                Classroom.id == classroom_id,
                Classroom.teacher_id == user.id
            )
        )
    )
    if not classroom_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    # Get enrollments
    enrollments_result = await db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.classroom_id == classroom_id,
                Enrollment.is_active == True
            )
        )
    )
    enrollments = enrollments_result.scalars().all()
    
    total_students = len(enrollments)
    today = datetime.utcnow().date()
    
    logger.info(f"Fetching stats for classroom {classroom_id}")

    # Pre-fetch all skills for name mapping
    skills_result = await db.execute(select(Skill))
    all_skills = {skill.id: skill.display_name for skill in skills_result.scalars().all()}

    # Get all student IDs
    student_ids = [e.student_id for e in enrollments]
    enrollment_map = {e.student_id: e for e in enrollments}

    # BATCH QUERY 1: Get all students in one query
    students_result = await db.execute(
        select(User).where(User.id.in_(student_ids))
    )
    students_map = {s.id: s for s in students_result.scalars().all()}

    # BATCH QUERY 2: Get all attempts for all students with aggregation
    from sqlalchemy import case
    attempts_agg = await db.execute(
        select(
            QuestionAttempt.user_id,
            func.count(QuestionAttempt.id).label('total'),
            func.sum(case((QuestionAttempt.is_correct, 1), else_=0)).label('correct'),
            func.sum(func.coalesce(QuestionAttempt.time_taken_seconds, 0)).label('time_seconds'),
            func.sum(case((func.date(QuestionAttempt.attempted_at) == today, 1), else_=0)).label('today_count')
        )
        .where(QuestionAttempt.user_id.in_(student_ids))
        .group_by(QuestionAttempt.user_id)
    )
    attempts_map = {row.user_id: row for row in attempts_agg.all()}

    # BATCH QUERY 3: Get all skill progress for all students
    skill_progress_result = await db.execute(
        select(SkillProgress).where(SkillProgress.user_id.in_(student_ids))
    )
    # Group skill progress by user_id
    skill_progress_by_user: dict[UUID, list] = {}
    for sp in skill_progress_result.scalars().all():
        if sp.user_id not in skill_progress_by_user:
            skill_progress_by_user[sp.user_id] = []
        skill_progress_by_user[sp.user_id].append(sp)

    # Aggregate skill data for classroom breakdown
    classroom_skill_data: dict[str, list[float]] = {}

    # Process results
    active_today = 0
    total_accuracy = 0
    total_questions = 0
    total_time_seconds = 0
    student_progress_list = []

    for student_id in student_ids:
        student = students_map.get(student_id)
        if not student:
            continue

        enrollment = enrollment_map[student_id]
        attempts_data = attempts_map.get(student_id)

        questions_attempted = attempts_data.total if attempts_data else 0
        questions_correct = attempts_data.correct if attempts_data else 0
        student_time_seconds = attempts_data.time_seconds if attempts_data else 0
        today_count = attempts_data.today_count if attempts_data else 0

        accuracy = questions_correct / questions_attempted if questions_attempted > 0 else 0

        total_time_seconds += student_time_seconds
        if today_count > 0:
            active_today += 1

        total_questions += questions_attempted
        total_accuracy += accuracy

        # Build mastery_levels with skill names
        mastery_levels: dict[str, float] = {}
        for sp in skill_progress_by_user.get(student_id, []):
            skill_name = all_skills.get(sp.skill_id, f"Skill {sp.skill_id}")
            mastery_levels[skill_name] = sp.mastery_level

            if skill_name not in classroom_skill_data:
                classroom_skill_data[skill_name] = []
            classroom_skill_data[skill_name].append(sp.mastery_level)

        student_progress_list.append(StudentProgress(
            student_id=student.id,
            student_name=student.display_name,
            avatar_url=student.avatar_url,
            questions_attempted=questions_attempted,
            questions_correct=questions_correct,
            accuracy_rate=accuracy,
            time_spent_minutes=student_time_seconds // 60,
            last_active=enrollment.last_activity_at,
            streak_days=student.streak_days,
            mastery_levels=mastery_levels
        ))

    # Calculate classroom-wide skill breakdown (average mastery per skill)
    skill_breakdown: dict[str, float] = {}
    for skill_name, mastery_values in classroom_skill_data.items():
        if mastery_values:
            skill_breakdown[skill_name] = sum(mastery_values) / len(mastery_values)

    # Sort for top/struggling
    sorted_by_accuracy = sorted(student_progress_list, key=lambda x: x.accuracy_rate, reverse=True)
    top_performers = sorted_by_accuracy[:5]
    struggling = sorted_by_accuracy[-5:] if len(sorted_by_accuracy) > 5 else []

    avg_accuracy = total_accuracy / total_students if total_students > 0 else 0
    avg_questions = total_questions / total_students if total_students > 0 else 0

    return ClassroomStats(
        classroom_id=classroom_id,
        total_students=total_students,
        active_students_today=active_today,
        average_accuracy=avg_accuracy,
        average_questions_per_student=avg_questions,
        total_questions_answered=total_questions,
        top_performers=top_performers,
        struggling_students=struggling,
        skill_breakdown=skill_breakdown
    )


# Student endpoint to join a classroom
@router.post("/join", response_model=EnrollmentResponse)
async def join_classroom(
    data: JoinClassroom,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a classroom using a join code"""
    # Find classroom
    result = await db.execute(
        select(Classroom).where(
            and_(
                Classroom.join_code == data.join_code.upper(),
                Classroom.is_active == True,
                Classroom.allow_self_enroll == True
            )
        )
    )
    classroom = result.scalar_one_or_none()
    
    if not classroom:
        raise HTTPException(status_code=404, detail="Invalid join code or classroom not accepting students")
    
    # Check if already enrolled
    existing = await db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.classroom_id == classroom.id,
                Enrollment.student_id == user.id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already enrolled in this classroom")
    
    # Check capacity
    count_result = await db.execute(
        select(func.count(Enrollment.id)).where(
            and_(
                Enrollment.classroom_id == classroom.id,
                Enrollment.is_active == True
            )
        )
    )
    current_count = count_result.scalar() or 0
    
    if current_count >= classroom.max_students:
        raise HTTPException(status_code=400, detail="Classroom is full")
    
    # Create enrollment
    enrollment = Enrollment(
        classroom_id=classroom.id,
        student_id=user.id,
        status=EnrollmentStatus.ACTIVE,
        is_active=True
    )
    
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    
    return EnrollmentResponse(
        id=enrollment.id,
        classroom_id=enrollment.classroom_id,
        student_id=enrollment.student_id,
        student_name=user.display_name,
        student_email=user.email,
        status=enrollment.status.value,
        is_active=enrollment.is_active,
        assignments_completed=0,
        total_score=0,
        enrolled_at=enrollment.enrolled_at,
        last_activity_at=None
    )
