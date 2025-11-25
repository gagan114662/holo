"""
Knowledge Graph - Concept Mastery Tracking
Tracks student understanding across interconnected concepts.

Key differentiator: Not just question counts, but true concept mastery
with prerequisite tracking and learning path optimization.
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class MasteryLevel(Enum):
    """Mastery levels for concepts"""
    UNKNOWN = 0        # Never encountered
    NOVICE = 1         # Just introduced
    DEVELOPING = 2     # Some understanding
    PROFICIENT = 3     # Good understanding
    ADVANCED = 4       # Deep understanding
    MASTERED = 5       # Complete mastery


@dataclass
class Concept:
    """A single concept in the knowledge graph"""
    id: str
    name: str
    subject: str
    grade_level: str
    description: str = ""
    prerequisites: list[str] = field(default_factory=list)  # Concept IDs
    related_concepts: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    difficulty: int = 1  # 1-5


@dataclass
class ConceptMastery:
    """A student's mastery of a concept"""
    concept_id: str
    level: MasteryLevel
    confidence: float  # 0-1, decays over time
    attempts: int
    correct: int
    last_practiced: datetime
    last_assessed: datetime
    misconceptions: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class LearningPath:
    """Recommended learning path for a student"""
    concepts: list[str]  # Ordered concept IDs
    reason: str
    estimated_time_minutes: int
    prerequisites_met: bool


class KnowledgeGraph:
    """
    Knowledge graph for tracking concept mastery.

    Features:
    - Concept relationships (prerequisites, related)
    - Mastery tracking with confidence decay
    - Learning path optimization
    - Misconception tracking
    - Spaced repetition scheduling
    """

    def __init__(self):
        # Concept definitions
        self.concepts: dict[str, Concept] = {}
        # User mastery: user_id -> concept_id -> ConceptMastery
        self.user_mastery: dict[str, dict[str, ConceptMastery]] = defaultdict(dict)
        self._lock = asyncio.Lock()

        # Initialize with curriculum concepts
        self._load_curriculum()

    def _load_curriculum(self):
        """Load standard curriculum concepts"""
        # Math concepts
        math_concepts = [
            Concept("math_addition", "Addition", "math", "K-2",
                   "Combining quantities", [], ["math_subtraction"], ["add", "plus", "sum"]),
            Concept("math_subtraction", "Subtraction", "math", "K-2",
                   "Taking away quantities", ["math_addition"], ["math_addition"], ["subtract", "minus", "difference"]),
            Concept("math_multiplication", "Multiplication", "math", "3-5",
                   "Repeated addition", ["math_addition"], ["math_division"], ["multiply", "times", "product"]),
            Concept("math_division", "Division", "math", "3-5",
                   "Splitting into equal groups", ["math_multiplication"], ["math_multiplication"], ["divide", "quotient"]),
            Concept("math_fractions", "Fractions", "math", "3-5",
                   "Parts of a whole", ["math_division"], ["math_decimals"], ["fraction", "numerator", "denominator"]),
            Concept("math_decimals", "Decimals", "math", "4-6",
                   "Base-10 fractions", ["math_fractions"], ["math_percentages"], ["decimal", "point"]),
            Concept("math_percentages", "Percentages", "math", "5-7",
                   "Parts per hundred", ["math_decimals", "math_fractions"], [], ["percent", "percentage"]),
            Concept("math_algebra_basic", "Basic Algebra", "math", "6-8",
                   "Using variables", ["math_multiplication", "math_division"], ["math_equations"], ["variable", "expression"]),
            Concept("math_equations", "Equations", "math", "6-8",
                   "Solving for unknowns", ["math_algebra_basic"], ["math_inequalities"], ["equation", "solve"]),
            Concept("math_geometry_basic", "Basic Geometry", "math", "3-5",
                   "Shapes and properties", [], ["math_geometry_area"], ["shape", "angle", "side"]),
            Concept("math_geometry_area", "Area and Perimeter", "math", "4-6",
                   "Measuring 2D space", ["math_geometry_basic", "math_multiplication"], [], ["area", "perimeter"]),
        ]

        # Science concepts
        science_concepts = [
            Concept("sci_matter", "States of Matter", "science", "3-5",
                   "Solid, liquid, gas", [], ["sci_atoms"], ["matter", "solid", "liquid", "gas"]),
            Concept("sci_atoms", "Atoms and Molecules", "science", "6-8",
                   "Building blocks of matter", ["sci_matter"], ["sci_elements"], ["atom", "molecule"]),
            Concept("sci_elements", "Elements", "science", "6-8",
                   "Pure substances", ["sci_atoms"], ["sci_compounds"], ["element", "periodic table"]),
            Concept("sci_compounds", "Compounds", "science", "6-8",
                   "Combined elements", ["sci_elements"], [], ["compound", "formula"]),
            Concept("sci_cells", "Cells", "science", "5-7",
                   "Basic unit of life", [], ["sci_cell_parts"], ["cell", "organism"]),
            Concept("sci_cell_parts", "Cell Structure", "science", "6-8",
                   "Parts of a cell", ["sci_cells"], ["sci_dna"], ["nucleus", "membrane", "organelle"]),
            Concept("sci_dna", "DNA and Genetics", "science", "7-9",
                   "Genetic information", ["sci_cell_parts"], [], ["dna", "gene", "chromosome"]),
            Concept("sci_photosynthesis", "Photosynthesis", "science", "5-7",
                   "How plants make food", ["sci_cells"], [], ["photosynthesis", "chlorophyll"]),
            Concept("sci_energy", "Energy", "science", "4-6",
                   "Ability to do work", [], ["sci_energy_types"], ["energy", "work"]),
            Concept("sci_energy_types", "Types of Energy", "science", "5-7",
                   "Different energy forms", ["sci_energy"], ["sci_energy_transfer"], ["kinetic", "potential"]),
            Concept("sci_forces", "Forces", "science", "4-6",
                   "Pushes and pulls", [], ["sci_motion"], ["force", "push", "pull"]),
            Concept("sci_motion", "Motion", "science", "5-7",
                   "Movement of objects", ["sci_forces"], ["sci_newtons_laws"], ["motion", "speed", "velocity"]),
            Concept("sci_newtons_laws", "Newton's Laws", "science", "7-9",
                   "Laws of motion", ["sci_motion", "sci_forces"], [], ["newton", "inertia", "acceleration"]),
        ]

        # Literature concepts
        lit_concepts = [
            Concept("lit_plot", "Plot Structure", "literature", "4-8",
                   "Story sequence", [], ["lit_conflict"], ["plot", "beginning", "middle", "end"]),
            Concept("lit_conflict", "Conflict", "literature", "5-8",
                   "Story problems", ["lit_plot"], ["lit_resolution"], ["conflict", "problem"]),
            Concept("lit_resolution", "Resolution", "literature", "5-8",
                   "How conflict is solved", ["lit_conflict"], [], ["resolution", "solution"]),
            Concept("lit_character", "Character Development", "literature", "4-8",
                   "How characters change", [], ["lit_motivation"], ["character", "protagonist"]),
            Concept("lit_motivation", "Character Motivation", "literature", "5-9",
                   "Why characters act", ["lit_character"], [], ["motivation", "reason"]),
            Concept("lit_theme", "Theme", "literature", "5-9",
                   "Central message", ["lit_plot"], [], ["theme", "message", "lesson"]),
            Concept("lit_figurative", "Figurative Language", "literature", "4-8",
                   "Non-literal language", [], ["lit_metaphor", "lit_simile"], ["figurative"]),
            Concept("lit_metaphor", "Metaphor", "literature", "5-8",
                   "Comparison without like/as", ["lit_figurative"], [], ["metaphor"]),
            Concept("lit_simile", "Simile", "literature", "4-7",
                   "Comparison using like/as", ["lit_figurative"], [], ["simile", "like", "as"]),
        ]

        # Load all concepts
        for concept in math_concepts + science_concepts + lit_concepts:
            self.concepts[concept.id] = concept

    async def get_mastery(
        self,
        user_id: str,
        concept_id: str
    ) -> Optional[ConceptMastery]:
        """Get a user's mastery of a specific concept"""
        async with self._lock:
            return self.user_mastery.get(user_id, {}).get(concept_id)

    async def update_mastery(
        self,
        user_id: str,
        concept_id: str,
        is_correct: bool,
        confidence_delta: float = 0.1
    ) -> ConceptMastery:
        """Update mastery based on a question attempt"""
        async with self._lock:
            if user_id not in self.user_mastery:
                self.user_mastery[user_id] = {}

            mastery = self.user_mastery[user_id].get(concept_id)
            now = datetime.utcnow()

            if mastery is None:
                mastery = ConceptMastery(
                    concept_id=concept_id,
                    level=MasteryLevel.NOVICE,
                    confidence=0.3,
                    attempts=0,
                    correct=0,
                    last_practiced=now,
                    last_assessed=now
                )

            # Update counts
            mastery.attempts += 1
            if is_correct:
                mastery.correct += 1
                mastery.confidence = min(1.0, mastery.confidence + confidence_delta)
            else:
                mastery.confidence = max(0.0, mastery.confidence - confidence_delta * 1.5)

            mastery.last_practiced = now

            # Update level based on accuracy and attempts
            accuracy = mastery.correct / mastery.attempts if mastery.attempts > 0 else 0
            mastery.level = self._calculate_level(accuracy, mastery.attempts, mastery.confidence)

            self.user_mastery[user_id][concept_id] = mastery
            return mastery

    def _calculate_level(
        self,
        accuracy: float,
        attempts: int,
        confidence: float
    ) -> MasteryLevel:
        """Calculate mastery level from metrics"""
        if attempts < 2:
            return MasteryLevel.NOVICE

        # Combined score
        score = (accuracy * 0.5 + confidence * 0.3 + min(attempts / 20, 1) * 0.2)

        if score >= 0.9 and attempts >= 10:
            return MasteryLevel.MASTERED
        elif score >= 0.75 and attempts >= 5:
            return MasteryLevel.ADVANCED
        elif score >= 0.6 and attempts >= 3:
            return MasteryLevel.PROFICIENT
        elif score >= 0.4:
            return MasteryLevel.DEVELOPING
        else:
            return MasteryLevel.NOVICE

    async def get_recommended_concepts(
        self,
        user_id: str,
        subject: Optional[str] = None,
        limit: int = 5
    ) -> list[LearningPath]:
        """Get recommended concepts to study next"""
        async with self._lock:
            user_data = self.user_mastery.get(user_id, {})

        recommendations = []

        for concept_id, concept in self.concepts.items():
            if subject and concept.subject != subject:
                continue

            mastery = user_data.get(concept_id)

            # Check prerequisites
            prereqs_met = all(
                user_data.get(p, ConceptMastery(p, MasteryLevel.UNKNOWN, 0, 0, 0, datetime.utcnow(), datetime.utcnow())).level.value >= MasteryLevel.DEVELOPING.value
                for p in concept.prerequisites
            )

            # Calculate priority score
            priority = 0

            if mastery is None:
                # New concept
                if prereqs_met:
                    priority = 0.8
                else:
                    priority = 0.2
            else:
                # Existing concept - consider decay
                days_since = (datetime.utcnow() - mastery.last_practiced).days
                decay = min(days_since / 30, 1.0)  # Full decay after 30 days

                if mastery.level.value < MasteryLevel.PROFICIENT.value:
                    priority = 0.9 - (mastery.level.value * 0.1) + (decay * 0.2)
                elif decay > 0.5:
                    # Spaced repetition - review if decaying
                    priority = 0.5 + (decay * 0.3)
                else:
                    priority = 0.1

            if priority > 0.3:
                recommendations.append({
                    "concept": concept,
                    "priority": priority,
                    "prereqs_met": prereqs_met,
                    "current_level": mastery.level if mastery else MasteryLevel.UNKNOWN
                })

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)

        # Convert to LearningPaths
        paths = []
        for rec in recommendations[:limit]:
            concept = rec["concept"]
            paths.append(LearningPath(
                concepts=[concept.id],
                reason=self._get_recommendation_reason(rec),
                estimated_time_minutes=10 + (concept.difficulty * 5),
                prerequisites_met=rec["prereqs_met"]
            ))

        return paths

    def _get_recommendation_reason(self, rec: dict) -> str:
        """Generate reason for recommendation"""
        level = rec["current_level"]
        concept = rec["concept"]

        if level == MasteryLevel.UNKNOWN:
            if rec["prereqs_met"]:
                return f"Ready to learn {concept.name} - prerequisites completed!"
            else:
                return f"Foundation concept for future learning"
        elif level.value < MasteryLevel.PROFICIENT.value:
            return f"Keep practicing {concept.name} to strengthen understanding"
        else:
            return f"Review {concept.name} to maintain mastery"

    async def get_user_stats(self, user_id: str) -> dict:
        """Get comprehensive stats for a user"""
        async with self._lock:
            user_data = self.user_mastery.get(user_id, {})

        total_concepts = len(self.concepts)
        practiced = len(user_data)
        mastered = sum(1 for m in user_data.values() if m.level == MasteryLevel.MASTERED)
        proficient = sum(1 for m in user_data.values() if m.level.value >= MasteryLevel.PROFICIENT.value)

        # By subject
        by_subject = defaultdict(lambda: {"total": 0, "practiced": 0, "mastered": 0})
        for concept_id, concept in self.concepts.items():
            by_subject[concept.subject]["total"] += 1
            if concept_id in user_data:
                by_subject[concept.subject]["practiced"] += 1
                if user_data[concept_id].level == MasteryLevel.MASTERED:
                    by_subject[concept.subject]["mastered"] += 1

        # Calculate overall score
        if practiced > 0:
            total_score = sum(m.level.value for m in user_data.values())
            avg_level = total_score / practiced
        else:
            avg_level = 0

        return {
            "total_concepts": total_concepts,
            "concepts_practiced": practiced,
            "concepts_mastered": mastered,
            "concepts_proficient": proficient,
            "progress_percentage": (practiced / total_concepts * 100) if total_concepts > 0 else 0,
            "mastery_percentage": (mastered / total_concepts * 100) if total_concepts > 0 else 0,
            "average_level": avg_level,
            "by_subject": dict(by_subject),
            "strengths": self._identify_strengths(user_data),
            "areas_for_improvement": self._identify_weaknesses(user_data)
        }

    def _identify_strengths(self, user_data: dict) -> list[str]:
        """Identify user's strongest concepts"""
        strong = [
            (cid, m) for cid, m in user_data.items()
            if m.level.value >= MasteryLevel.ADVANCED.value
        ]
        strong.sort(key=lambda x: (x[1].level.value, x[1].confidence), reverse=True)
        return [
            self.concepts[cid].name for cid, _ in strong[:5]
            if cid in self.concepts
        ]

    def _identify_weaknesses(self, user_data: dict) -> list[str]:
        """Identify concepts needing work"""
        weak = [
            (cid, m) for cid, m in user_data.items()
            if m.level.value <= MasteryLevel.DEVELOPING.value and m.attempts >= 2
        ]
        weak.sort(key=lambda x: (x[1].level.value, x[1].confidence))
        return [
            self.concepts[cid].name for cid, _ in weak[:5]
            if cid in self.concepts
        ]

    async def record_misconception(
        self,
        user_id: str,
        concept_id: str,
        misconception: str
    ):
        """Record a misconception for later addressing"""
        async with self._lock:
            if user_id not in self.user_mastery:
                return

            mastery = self.user_mastery[user_id].get(concept_id)
            if mastery and misconception not in mastery.misconceptions:
                mastery.misconceptions.append(misconception)

    async def find_concept_by_keyword(self, keyword: str) -> list[Concept]:
        """Find concepts matching a keyword"""
        keyword = keyword.lower()
        matches = []
        for concept in self.concepts.values():
            if (keyword in concept.name.lower() or
                keyword in concept.description.lower() or
                any(keyword in kw.lower() for kw in concept.keywords)):
                matches.append(concept)
        return matches


# Global instance
knowledge_graph = KnowledgeGraph()
