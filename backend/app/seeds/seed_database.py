"""
Database seeder script
Seeds the database with subjects, skills, and questions
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import seed data
from .subjects import SUBJECTS
from .questions_math import ALL_MATH_QUESTIONS
from .questions_science import ALL_SCIENCE_QUESTIONS
from .questions_humanities import ALL_HUMANITIES_QUESTIONS
from .questions_cs import ALL_CS_QUESTIONS

# Import models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..models.question import Subject, Skill, Question, QuestionType, DifficultyLevel
from ..config import settings
from ..database import Base


async def seed_subjects_and_skills(session: AsyncSession) -> dict:
    """Seed subjects and skills, return mapping of name -> id"""
    subject_map = {}
    skill_map = {}
    
    for subject_data in SUBJECTS:
        # Check if subject exists
        result = await session.execute(
            select(Subject).where(Subject.name == subject_data["name"])
        )
        subject = result.scalar_one_or_none()
        
        if not subject:
            subject = Subject(
                name=subject_data["name"],
                slug=subject_data["name"].lower().replace(" ", "-"),
                display_name=subject_data["display_name"],
                description=subject_data["description"],
                icon=subject_data["icon"],
                color=subject_data["color"],
            )
            session.add(subject)
            await session.flush()
        
        subject_map[subject_data["name"]] = subject.id
        
        # Add skills for this subject
        for skill_data in subject_data["skills"]:
            skill_key = f"{subject_data['name']}_{skill_data['name']}"
            
            result = await session.execute(
                select(Skill).where(
                    Skill.name == skill_data["name"],
                    Skill.subject_id == subject.id
                )
            )
            skill = result.scalar_one_or_none()
            
            if not skill:
                skill = Skill(
                    subject_id=subject.id,
                    name=skill_data["name"],
                    slug=skill_data["name"].lower().replace(" ", "-"),
                    display_name=skill_data["display_name"],
                    order_index=skill_data["order"],
                )
                session.add(skill)
                await session.flush()
            
            skill_map[skill_key] = skill.id
    
    await session.commit()
    print(f"✓ Seeded {len(subject_map)} subjects and {len(skill_map)} skills")
    return subject_map, skill_map


async def seed_questions(session: AsyncSession, subject_map: dict, skill_map: dict):
    """Seed all questions"""
    
    # Map subject name to questions
    question_sets = {
        "mathematics": ALL_MATH_QUESTIONS,
        "physics": [q for q in ALL_SCIENCE_QUESTIONS if q.get("skill") in [
            "motion_basics", "velocity_acceleration", "forces", "newtons_laws",
            "work_energy", "momentum", "gravity", "waves", "sound", "light_optics",
            "electricity", "magnetism", "thermodynamics"
        ]],
        "chemistry": [q for q in ALL_SCIENCE_QUESTIONS if q.get("skill") in [
            "atomic_structure", "periodic_table", "chemical_bonding", "chemical_equations",
            "stoichiometry", "states_of_matter", "solutions", "acids_bases",
            "redox_reactions", "organic_chemistry"
        ]],
        "biology": [q for q in ALL_SCIENCE_QUESTIONS if q.get("skill") in [
            "cell_structure", "cell_processes", "genetics_basics", "dna_rna",
            "heredity", "evolution", "classification", "ecosystems", "human_body", "plants"
        ]],
        "literature": [q for q in ALL_HUMANITIES_QUESTIONS if q.get("skill") in [
            "reading_comprehension", "vocabulary", "grammar", "literary_devices",
            "poetry_analysis", "fiction_analysis", "essay_writing", "creative_writing"
        ]],
        "history": [q for q in ALL_HUMANITIES_QUESTIONS if q.get("skill") in [
            "ancient_civilizations", "classical_era", "medieval_period", "renaissance",
            "age_of_exploration", "revolutions", "world_wars", "modern_history"
        ]],
        "philosophy": [q for q in ALL_HUMANITIES_QUESTIONS if q.get("skill") in [
            "logic_basics", "arguments", "ethics_basics", "philosophical_questions", "critical_thinking"
        ]],
        "computer_science": ALL_CS_QUESTIONS,
    }
    
    total_count = 0
    
    for subject_name, questions in question_sets.items():
        subject_id = subject_map.get(subject_name)
        if not subject_id:
            print(f"⚠ Subject not found: {subject_name}")
            continue
        
        count = 0
        for q_data in questions:
            skill_key = f"{subject_name}_{q_data['skill']}"
            skill_id = skill_map.get(skill_key)
            
            # Map question type
            q_type_map = {
                "numeric": QuestionType.NUMERIC,
                "free_text": QuestionType.FREE_TEXT,
                "multiple_choice": QuestionType.MULTIPLE_CHOICE,
            }
            q_type = q_type_map.get(q_data.get("type", "free_text"), QuestionType.FREE_TEXT)
            
            # Map difficulty
            diff_map = {
                "easy": DifficultyLevel.EASY,
                "medium": DifficultyLevel.MEDIUM,
                "hard": DifficultyLevel.HARD,
                "expert": DifficultyLevel.EXPERT,
            }
            difficulty = diff_map.get(q_data.get("difficulty", "medium"), DifficultyLevel.MEDIUM)
            
            # Check if question already exists (by text)
            result = await session.execute(
                select(Question).where(
                    Question.content == q_data["question"],
                    Question.subject_id == subject_id
                )
            )
            if result.scalar_one_or_none():
                continue

            # Build extra_data
            extra_data = {}
            if q_data.get("acceptable_answers"):
                extra_data["acceptable_answers"] = q_data["acceptable_answers"]

            question = Question(
                subject_id=subject_id,
                skill_id=skill_id,
                content=q_data["question"],
                question_type=q_type,
                difficulty=difficulty,
                options=q_data.get("options"),
                correct_answer=q_data["answer"],
                explanation=q_data["explanation"],
                extra_data=extra_data if extra_data else None,
            )
            session.add(question)
            count += 1
        
        await session.flush()
        total_count += count
        print(f"  ✓ {subject_name}: {count} questions")
    
    await session.commit()
    print(f"✓ Total: {total_count} questions seeded")
    return total_count


async def main():
    """Main seeder function"""
    print("=" * 50)
    print("HoloTutor Database Seeder")
    print("=" * 50)
    
    # Create engine and tables
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Seed subjects and skills
            print("\n📚 Seeding subjects and skills...")
            subject_map, skill_map = await seed_subjects_and_skills(session)
            
            # Seed questions
            print("\n❓ Seeding questions...")
            total = await seed_questions(session, subject_map, skill_map)
            
            print("\n" + "=" * 50)
            print(f"✅ Seeding complete! {total} questions added.")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
