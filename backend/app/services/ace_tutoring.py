"""
ACE Tutoring Service
Self-improving AI tutor using Agentic Context Engine
Learns from successful teaching interactions to improve over time
"""
import os
import json
import logging
from typing import Optional
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)

# Playbook storage location
PLAYBOOK_DIR = Path(__file__).parent.parent.parent / "playbooks"
PLAYBOOK_DIR.mkdir(exist_ok=True)


class ACETutoringService:
    """
    Adaptive tutoring service that learns from experience.
    Uses ACE framework to maintain a playbook of successful teaching strategies.
    """

    def __init__(self):
        self.ace_agent = None
        self.playbook_path = PLAYBOOK_DIR / "tutor_playbook.json"
        self._init_ace()

    def _init_ace(self):
        """Initialize ACE agent if available"""
        try:
            from ace import ACELiteLLM
            
            # Configure LLM provider (prefer Anthropic, fall back to OpenAI)
            if settings.anthropic_api_key:
                model = f"anthropic/{settings.anthropic_model}"
                os.environ.setdefault("ANTHROPIC_API_KEY", settings.anthropic_api_key)
            elif settings.openai_api_key:
                model = "openai/gpt-4o-mini"
                os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
            else:
                logger.warning("No AI API key configured, ACE tutoring disabled")
                return

            # Initialize ACE agent with tutor system prompt
            self.ace_agent = ACELiteLLM(
                model=model,
                system_prompt=self._get_tutor_system_prompt(),
            )

            # Load existing playbook if available
            if self.playbook_path.exists():
                try:
                    self.ace_agent = ACELiteLLM.from_playbook(
                        str(self.playbook_path),
                        model=model,
                        system_prompt=self._get_tutor_system_prompt(),
                    )
                    logger.info(f"Loaded tutor playbook from {self.playbook_path}")
                except Exception as e:
                    logger.warning(f"Could not load playbook: {e}")

            logger.info("ACE tutoring service initialized")

        except ImportError:
            logger.info("ACE framework not installed, using basic tutoring")
        except Exception as e:
            logger.error(f"Error initializing ACE: {e}")

    def _get_tutor_system_prompt(self) -> str:
        """Get the system prompt for the AI tutor"""
        return """You are an expert AI tutor who adapts your teaching style based on the student's needs.

TEACHING PRINCIPLES:
1. Be encouraging and supportive - celebrate progress
2. Use the Socratic method - ask guiding questions rather than giving answers directly
3. Adapt explanations to the student's level
4. Use analogies and real-world examples
5. Break complex topics into smaller, digestible pieces
6. When a student struggles, try a different approach
7. Build on what the student already knows

RESPONSE GUIDELINES:
- Keep responses concise but helpful (2-4 sentences for hints, longer for explanations)
- Use simple language appropriate for the student's grade level
- Include encouragement even when correcting mistakes
- Ask follow-up questions to check understanding

Learn from each interaction to improve your teaching strategies."""

    async def get_hint(
        self,
        question_content: str,
        correct_answer: str,
        student_attempt: Optional[str] = None,
        subject: str = "general",
        grade_level: int = 8,
    ) -> str:
        """
        Generate an adaptive hint for the student.
        Learns from successful hint patterns over time.
        """
        if not self.ace_agent:
            return self._fallback_hint(question_content, student_attempt)

        prompt = f"""
Subject: {subject}
Grade Level: {grade_level}
Question: {question_content}
Correct Answer (DO NOT reveal): {correct_answer}
Student's Previous Attempt: {student_attempt or "None yet"}

Provide a helpful hint that guides the student toward the answer without giving it away.
Use the Socratic method - ask a guiding question or point them in the right direction."""

        try:
            response = self.ace_agent.ask(prompt)
            return response
        except Exception as e:
            logger.error(f"ACE hint generation failed: {e}")
            return self._fallback_hint(question_content, student_attempt)

    async def explain_concept(
        self,
        topic: str,
        question_context: str,
        student_question: str,
        grade_level: int = 8,
    ) -> str:
        """
        Generate an explanation for a concept the student is struggling with.
        """
        if not self.ace_agent:
            return self._fallback_explanation(topic)

        prompt = f"""
Topic: {topic}
Related Question: {question_context}
Student's Question: {student_question}
Grade Level: {grade_level}

Explain this concept clearly and appropriately for a grade {grade_level} student.
Use analogies and examples they would understand."""

        try:
            response = self.ace_agent.ask(prompt)
            return response
        except Exception as e:
            logger.error(f"ACE explanation failed: {e}")
            return self._fallback_explanation(topic)

    async def generate_encouragement(
        self,
        was_correct: bool,
        streak: int = 0,
        subject: str = "general",
    ) -> str:
        """Generate personalized encouragement based on performance"""
        if not self.ace_agent:
            return self._fallback_encouragement(was_correct, streak)

        prompt = f"""
Result: {"Correct answer" if was_correct else "Incorrect answer"}
Current Streak: {streak} correct answers in a row
Subject: {subject}

Generate a brief, personalized encouragement message (1-2 sentences).
If incorrect, be supportive and motivating. If correct, celebrate appropriately."""

        try:
            response = self.ace_agent.ask(prompt)
            return response
        except Exception as e:
            logger.error(f"ACE encouragement failed: {e}")
            return self._fallback_encouragement(was_correct, streak)

    async def adapt_difficulty_recommendation(
        self,
        recent_accuracy: float,
        current_difficulty: str,
        questions_attempted: int,
    ) -> dict:
        """Recommend difficulty adjustments based on performance"""
        if not self.ace_agent:
            return self._fallback_difficulty_rec(recent_accuracy, current_difficulty)

        prompt = f"""
Recent Accuracy: {recent_accuracy * 100:.1f}%
Current Difficulty: {current_difficulty}
Questions Attempted: {questions_attempted}

Based on this performance data, recommend:
1. Should difficulty change? (increase/decrease/maintain)
2. Why?
3. Confidence (0-1)

Respond in JSON: {{"recommendation": "increase/decrease/maintain", "reason": "...", "confidence": 0.X}}"""

        try:
            response = self.ace_agent.ask(prompt)
            # Parse JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"ACE difficulty recommendation failed: {e}")

        return self._fallback_difficulty_rec(recent_accuracy, current_difficulty)

    def save_playbook(self):
        """Save the current playbook to persist learned strategies"""
        if self.ace_agent:
            try:
                self.ace_agent.save_playbook(str(self.playbook_path))
                logger.info(f"Saved tutor playbook to {self.playbook_path}")
            except Exception as e:
                logger.error(f"Failed to save playbook: {e}")

    def record_interaction_outcome(
        self,
        interaction_type: str,
        was_successful: bool,
        context: dict,
    ):
        """
        Record the outcome of an interaction to improve future responses.
        This helps ACE learn what teaching strategies work best.
        """
        # ACE learns automatically from the conversation flow
        # This method is for explicit feedback that can be used for analysis
        outcome_log = PLAYBOOK_DIR / "interaction_outcomes.jsonl"
        try:
            with open(outcome_log, "a") as f:
                entry = {
                    "type": interaction_type,
                    "successful": was_successful,
                    "context": context,
                }
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"Could not log interaction outcome: {e}")

    # Fallback methods for when ACE is not available

    def _fallback_hint(self, question: str, attempt: Optional[str]) -> str:
        """Provide a generic hint when ACE is unavailable"""
        hints = [
            "Think about what information the question is asking for.",
            "Try breaking the problem into smaller steps.",
            "What do you already know about this topic?",
            "Read the question carefully - what are the key words?",
            "Can you think of a similar problem you've solved before?",
        ]
        import random
        return random.choice(hints)

    def _fallback_explanation(self, topic: str) -> str:
        """Provide a generic explanation prompt when ACE is unavailable"""
        return f"Let me help you understand {topic} better. What specifically is confusing you?"

    def _fallback_encouragement(self, was_correct: bool, streak: int) -> str:
        """Provide generic encouragement when ACE is unavailable"""
        if was_correct:
            if streak >= 5:
                return "Amazing streak! You're on fire! 🔥"
            elif streak >= 3:
                return "Great job! You're really getting the hang of this!"
            else:
                return "Correct! Well done!"
        else:
            return "Not quite, but don't give up! Every mistake is a learning opportunity."

    def _fallback_difficulty_rec(self, accuracy: float, current: str) -> dict:
        """Provide simple difficulty recommendation when ACE is unavailable"""
        if accuracy >= 0.85 and current != "HARD":
            return {"recommendation": "increase", "reason": "High accuracy", "confidence": 0.7}
        elif accuracy <= 0.5 and current != "EASY":
            return {"recommendation": "decrease", "reason": "Low accuracy", "confidence": 0.7}
        return {"recommendation": "maintain", "reason": "Appropriate level", "confidence": 0.6}


# Singleton instance
ace_tutor = ACETutoringService()
