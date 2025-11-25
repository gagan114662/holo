"""
Socratic Engine - Intelligent Question-Asking AI
Key differentiator: AI that teaches by asking, not just answering.

Based on the Socratic method:
1. Ask probing questions to reveal gaps in understanding
2. Guide students to discover answers themselves
3. Build critical thinking skills
4. Adapt questioning based on responses
"""
import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import anthropic

from ..config import settings

logger = logging.getLogger(__name__)


class QuestionType(Enum):
    """Types of Socratic questions"""
    CLARIFYING = "clarifying"           # "What do you mean by...?"
    PROBING_ASSUMPTIONS = "probing"     # "Why do you think that's true?"
    PROBING_EVIDENCE = "evidence"       # "What evidence supports this?"
    EXPLORING_VIEWPOINTS = "viewpoints" # "How might someone else see this?"
    PROBING_IMPLICATIONS = "implications" # "What would happen if...?"
    META_QUESTION = "meta"              # "Why is this question important?"


class ResponseQuality(Enum):
    """Quality of student response"""
    EXCELLENT = "excellent"     # Deep understanding shown
    GOOD = "good"              # Solid understanding
    PARTIAL = "partial"        # Some understanding, gaps present
    CONFUSED = "confused"      # Misconceptions present
    OFF_TOPIC = "off_topic"    # Didn't address the question
    NO_RESPONSE = "no_response"


@dataclass
class SocraticQuestion:
    """A Socratic question with context"""
    question: str
    question_type: QuestionType
    target_concept: str
    difficulty: int  # 1-5
    hints: list[str] = field(default_factory=list)
    follow_ups: list[str] = field(default_factory=list)


@dataclass
class SocraticExchange:
    """A single question-response exchange"""
    question: SocraticQuestion
    student_response: Optional[str] = None
    response_quality: Optional[ResponseQuality] = None
    feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SocraticDialogue:
    """A complete Socratic dialogue session"""
    id: str
    user_id: str
    topic: str
    subject: str
    grade_level: str
    exchanges: list[SocraticExchange] = field(default_factory=list)
    concepts_explored: list[str] = field(default_factory=list)
    understanding_level: float = 0.0  # 0-1
    started_at: datetime = field(default_factory=datetime.utcnow)


class SocraticEngine:
    """
    AI engine that teaches through questioning.

    Unlike traditional tutoring that provides answers,
    the Socratic Engine guides students to discover
    understanding through carefully crafted questions.
    """

    def __init__(self):
        self.anthropic_client = None
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key
            )

        self.active_dialogues: dict[str, SocraticDialogue] = {}
        self._lock = asyncio.Lock()

        # Question templates by type
        self.question_templates = {
            QuestionType.CLARIFYING: [
                "What do you mean when you say '{concept}'?",
                "Can you explain '{concept}' in your own words?",
                "How would you define '{concept}'?",
            ],
            QuestionType.PROBING_ASSUMPTIONS: [
                "Why do you believe that's true?",
                "What assumptions are you making here?",
                "Is that always the case? When might it not be?",
            ],
            QuestionType.PROBING_EVIDENCE: [
                "What evidence supports your thinking?",
                "How do you know that?",
                "Can you give an example?",
            ],
            QuestionType.EXPLORING_VIEWPOINTS: [
                "How might someone disagree with this?",
                "What's another way to look at this?",
                "What would {historical_figure} say about this?",
            ],
            QuestionType.PROBING_IMPLICATIONS: [
                "What would happen if {scenario}?",
                "What are the consequences of this?",
                "How does this connect to {related_concept}?",
            ],
            QuestionType.META_QUESTION: [
                "Why is understanding this important?",
                "How does this fit into the bigger picture?",
                "What questions does this raise for you?",
            ]
        }

    async def start_dialogue(
        self,
        user_id: str,
        topic: str,
        subject: str,
        grade_level: str,
        initial_understanding: Optional[str] = None
    ) -> SocraticDialogue:
        """
        Start a new Socratic dialogue on a topic.

        Args:
            user_id: Student's user ID
            topic: Topic to explore (e.g., "photosynthesis")
            subject: Subject area (e.g., "biology")
            grade_level: Student's grade level
            initial_understanding: Optional statement of current understanding

        Returns:
            SocraticDialogue with first question
        """
        import uuid
        dialogue_id = str(uuid.uuid4())

        dialogue = SocraticDialogue(
            id=dialogue_id,
            user_id=user_id,
            topic=topic,
            subject=subject,
            grade_level=grade_level
        )

        # Generate opening question
        opening = await self._generate_opening_question(
            topic, subject, grade_level, initial_understanding
        )

        dialogue.exchanges.append(SocraticExchange(question=opening))
        dialogue.concepts_explored.append(topic)

        async with self._lock:
            self.active_dialogues[dialogue_id] = dialogue

        return dialogue

    async def process_response(
        self,
        dialogue_id: str,
        student_response: str
    ) -> Optional[SocraticQuestion]:
        """
        Process student response and generate next question.

        Args:
            dialogue_id: ID of the dialogue
            student_response: Student's response to the last question

        Returns:
            Next SocraticQuestion or None if dialogue complete
        """
        async with self._lock:
            dialogue = self.active_dialogues.get(dialogue_id)

        if not dialogue or not dialogue.exchanges:
            return None

        # Get the current exchange
        current_exchange = dialogue.exchanges[-1]
        current_exchange.student_response = student_response

        # Analyze the response
        analysis = await self._analyze_response(
            dialogue, current_exchange, student_response
        )

        current_exchange.response_quality = analysis["quality"]
        current_exchange.feedback = analysis["feedback"]

        # Update understanding level
        dialogue.understanding_level = self._calculate_understanding(dialogue)

        # Determine if we should continue or conclude
        if self._should_conclude(dialogue, analysis):
            return None

        # Generate next question based on response
        next_question = await self._generate_follow_up(
            dialogue, current_exchange, analysis
        )

        if next_question:
            dialogue.exchanges.append(SocraticExchange(question=next_question))
            if next_question.target_concept not in dialogue.concepts_explored:
                dialogue.concepts_explored.append(next_question.target_concept)

        return next_question

    async def get_hint(self, dialogue_id: str) -> Optional[str]:
        """Get a hint for the current question"""
        async with self._lock:
            dialogue = self.active_dialogues.get(dialogue_id)

        if not dialogue or not dialogue.exchanges:
            return None

        current = dialogue.exchanges[-1]
        if current.question.hints:
            # Return next unused hint
            used_hints = len([e for e in dialogue.exchanges if e.feedback and "hint" in e.feedback.lower()])
            if used_hints < len(current.question.hints):
                return current.question.hints[used_hints]

        # Generate a hint if none available
        return await self._generate_hint(dialogue, current.question)

    async def _generate_opening_question(
        self,
        topic: str,
        subject: str,
        grade_level: str,
        initial_understanding: Optional[str]
    ) -> SocraticQuestion:
        """Generate the opening question for a dialogue"""

        if self.anthropic_client:
            prompt = f"""You are a Socratic tutor starting a dialogue about "{topic}" in {subject} for a {grade_level} student.

{f'The student says they understand: "{initial_understanding}"' if initial_understanding else 'The student is just starting to learn this topic.'}

Generate an opening Socratic question that:
1. Is appropriate for the grade level
2. Invites the student to share their thinking
3. Can reveal their current understanding level
4. Is engaging and not intimidating

Respond in JSON:
{{
    "question": "your opening question",
    "question_type": "clarifying|probing|evidence|viewpoints|implications|meta",
    "target_concept": "main concept being explored",
    "difficulty": 1-5,
    "hints": ["hint 1", "hint 2"],
    "follow_ups": ["possible follow-up 1", "possible follow-up 2"]
}}"""

            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )

                text = response.content[0].text
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    data = json.loads(json_match.group())
                    return SocraticQuestion(
                        question=data["question"],
                        question_type=QuestionType(data.get("question_type", "clarifying")),
                        target_concept=data.get("target_concept", topic),
                        difficulty=data.get("difficulty", 2),
                        hints=data.get("hints", []),
                        follow_ups=data.get("follow_ups", [])
                    )
            except Exception as e:
                logger.error(f"Failed to generate opening question: {e}")

        # Fallback question
        return SocraticQuestion(
            question=f"What do you already know about {topic}? Share your thoughts.",
            question_type=QuestionType.CLARIFYING,
            target_concept=topic,
            difficulty=1,
            hints=[f"Think about what you've heard about {topic}", "There's no wrong answer - just share what comes to mind"],
            follow_ups=[]
        )

    async def _analyze_response(
        self,
        dialogue: SocraticDialogue,
        exchange: SocraticExchange,
        response: str
    ) -> dict:
        """Analyze student response quality and understanding"""

        if self.anthropic_client:
            history = "\n".join([
                f"Q: {e.question.question}\nA: {e.student_response or '[no response]'}"
                for e in dialogue.exchanges[:-1]
            ])

            prompt = f"""Analyze this student's response in a Socratic dialogue about "{dialogue.topic}".

Previous exchanges:
{history}

Current question: {exchange.question.question}
Student response: {response}

Analyze:
1. Quality of response (excellent/good/partial/confused/off_topic)
2. What the response reveals about understanding
3. Misconceptions or gaps identified
4. Constructive feedback

Respond in JSON:
{{
    "quality": "excellent|good|partial|confused|off_topic",
    "understanding_indicators": ["what they understand"],
    "gaps": ["gaps or misconceptions"],
    "feedback": "brief constructive feedback",
    "next_focus": "what to explore next"
}}"""

            try:
                response_msg = await self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )

                text = response_msg.content[0].text
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    data = json.loads(json_match.group())
                    return {
                        "quality": ResponseQuality(data.get("quality", "partial")),
                        "understanding": data.get("understanding_indicators", []),
                        "gaps": data.get("gaps", []),
                        "feedback": data.get("feedback", ""),
                        "next_focus": data.get("next_focus", "")
                    }
            except Exception as e:
                logger.error(f"Failed to analyze response: {e}")

        # Fallback analysis
        word_count = len(response.split())
        if word_count < 5:
            quality = ResponseQuality.PARTIAL
        elif word_count > 50:
            quality = ResponseQuality.GOOD
        else:
            quality = ResponseQuality.PARTIAL

        return {
            "quality": quality,
            "understanding": [],
            "gaps": [],
            "feedback": "Thank you for sharing your thoughts.",
            "next_focus": dialogue.topic
        }

    async def _generate_follow_up(
        self,
        dialogue: SocraticDialogue,
        exchange: SocraticExchange,
        analysis: dict
    ) -> Optional[SocraticQuestion]:
        """Generate the next question based on response analysis"""

        if self.anthropic_client:
            prompt = f"""You are a Socratic tutor continuing a dialogue about "{dialogue.topic}".

The student just responded: "{exchange.student_response}"
Response quality: {analysis['quality'].value}
Feedback: {analysis['feedback']}
Gaps identified: {analysis.get('gaps', [])}
Next focus: {analysis.get('next_focus', dialogue.topic)}

Generate the next Socratic question that:
1. Builds on their response
2. Addresses any gaps or misconceptions
3. Deepens understanding
4. Maintains engagement

If their response was excellent, probe deeper.
If confused, step back and clarify.

Respond in JSON:
{{
    "question": "your next question",
    "question_type": "clarifying|probing|evidence|viewpoints|implications|meta",
    "target_concept": "concept being explored",
    "difficulty": 1-5,
    "hints": ["hint 1"],
    "follow_ups": ["follow-up 1"]
}}"""

            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}]
                )

                text = response.content[0].text
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    data = json.loads(json_match.group())
                    return SocraticQuestion(
                        question=data["question"],
                        question_type=QuestionType(data.get("question_type", "probing")),
                        target_concept=data.get("target_concept", dialogue.topic),
                        difficulty=data.get("difficulty", 2),
                        hints=data.get("hints", []),
                        follow_ups=data.get("follow_ups", [])
                    )
            except Exception as e:
                logger.error(f"Failed to generate follow-up: {e}")

        # Fallback
        return SocraticQuestion(
            question="Can you tell me more about that? What makes you think so?",
            question_type=QuestionType.PROBING_EVIDENCE,
            target_concept=dialogue.topic,
            difficulty=2,
            hints=[],
            follow_ups=[]
        )

    async def _generate_hint(
        self,
        dialogue: SocraticDialogue,
        question: SocraticQuestion
    ) -> str:
        """Generate a hint for the current question"""

        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=150,
                    messages=[{
                        "role": "user",
                        "content": f"Give a brief, helpful hint for this question without giving away the answer:\n\nQuestion: {question.question}\nTopic: {dialogue.topic}\n\nHint:"
                    }]
                )
                return response.content[0].text.strip()
            except Exception:
                pass

        return f"Think about what you know about {question.target_concept}. What comes to mind first?"

    def _calculate_understanding(self, dialogue: SocraticDialogue) -> float:
        """Calculate overall understanding level from exchanges"""
        if not dialogue.exchanges:
            return 0.0

        quality_scores = {
            ResponseQuality.EXCELLENT: 1.0,
            ResponseQuality.GOOD: 0.8,
            ResponseQuality.PARTIAL: 0.5,
            ResponseQuality.CONFUSED: 0.2,
            ResponseQuality.OFF_TOPIC: 0.1,
            ResponseQuality.NO_RESPONSE: 0.0
        }

        scored = [e for e in dialogue.exchanges if e.response_quality]
        if not scored:
            return 0.0

        # Weight recent responses more heavily
        total = 0
        weight_sum = 0
        for i, exchange in enumerate(scored):
            weight = 1 + (i * 0.5)  # Later responses weighted more
            total += quality_scores.get(exchange.response_quality, 0.5) * weight
            weight_sum += weight

        return total / weight_sum if weight_sum > 0 else 0.0

    def _should_conclude(self, dialogue: SocraticDialogue, analysis: dict) -> bool:
        """Determine if dialogue should conclude"""
        # Conclude after enough exchanges or high understanding
        if len(dialogue.exchanges) >= 10:
            return True
        if dialogue.understanding_level > 0.85 and len(dialogue.exchanges) >= 3:
            return True
        if analysis["quality"] == ResponseQuality.EXCELLENT and len(dialogue.exchanges) >= 5:
            return True
        return False

    async def get_summary(self, dialogue_id: str) -> Optional[dict]:
        """Get a summary of the dialogue"""
        async with self._lock:
            dialogue = self.active_dialogues.get(dialogue_id)

        if not dialogue:
            return None

        return {
            "topic": dialogue.topic,
            "subject": dialogue.subject,
            "exchanges_count": len(dialogue.exchanges),
            "concepts_explored": dialogue.concepts_explored,
            "understanding_level": dialogue.understanding_level,
            "duration_minutes": (datetime.utcnow() - dialogue.started_at).seconds / 60,
            "quality_progression": [
                e.response_quality.value if e.response_quality else None
                for e in dialogue.exchanges
            ]
        }


# Global instance
socratic_engine = SocraticEngine()
