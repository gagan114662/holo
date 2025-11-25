"""
Grading Service
Multi-layer intelligent grading with AI fallback
"""
import re
import math
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.question import Question, QuestionType


class GradingService:
    """
    Multi-layer grading system:
    1. Exact match (fast)
    2. Normalized match (handles case, whitespace, punctuation)
    3. Numeric tolerance (for math answers)
    4. Multiple acceptable answers
    5. AI semantic grading (for complex answers)
    """
    
    def __init__(self):
        self.anthropic_client = None
        if settings.anthropic_api_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            except ImportError:
                pass
    
    async def grade_answer(
        self,
        question: Question,
        student_answer: str,
        db: AsyncSession = None
    ) -> dict:
        """
        Grade a student's answer using multi-layer evaluation
        Returns: {is_correct: bool, is_partial: bool, score: float, feedback: str}
        """
        student_answer = student_answer.strip()
        correct_answer = question.correct_answer.strip()
        
        # Layer 1: Exact match
        if student_answer == correct_answer:
            return {
                "is_correct": True,
                "is_partial": False,
                "score": 1.0,
                "feedback": "Perfect! That's exactly right!"
            }
        
        # Layer 2: Normalized match
        normalized_student = self._normalize(student_answer)
        normalized_correct = self._normalize(correct_answer)
        
        if normalized_student == normalized_correct:
            return {
                "is_correct": True,
                "is_partial": False,
                "score": 1.0,
                "feedback": "Correct! Great job!"
            }
        
        # Layer 3: Check multiple acceptable answers (if stored in metadata)
        if question.metadata and "acceptable_answers" in question.metadata:
            for alt_answer in question.metadata["acceptable_answers"]:
                if self._normalize(student_answer) == self._normalize(alt_answer):
                    return {
                        "is_correct": True,
                        "is_partial": False,
                        "score": 1.0,
                        "feedback": "Correct! That's a valid answer!"
                    }
        
        # Layer 4: Numeric tolerance (for math/science)
        if question.question_type == QuestionType.NUMERIC:
            numeric_result = self._grade_numeric(student_answer, correct_answer)
            if numeric_result:
                return numeric_result
        
        # Layer 5: Multiple choice validation
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            return self._grade_multiple_choice(student_answer, correct_answer, question.options)
        
        # Layer 6: Partial match for free text
        if question.question_type == QuestionType.FREE_TEXT:
            partial_result = self._check_partial_match(student_answer, correct_answer)
            if partial_result["is_partial"]:
                return partial_result
        
        # Layer 7: AI semantic grading (if available and needed)
        if self.anthropic_client and question.question_type in [QuestionType.FREE_TEXT, QuestionType.ESSAY]:
            ai_result = await self._grade_with_ai(question, student_answer)
            if ai_result:
                return ai_result
        
        # Default: incorrect
        return {
            "is_correct": False,
            "is_partial": False,
            "score": 0.0,
            "feedback": self._generate_feedback(question, student_answer, correct_answer)
        }
    
    def _normalize(self, text: str) -> str:
        """Normalize text for comparison"""
        # Lowercase
        text = text.lower()
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove common punctuation
        text = re.sub(r'[.,;:!?\'"-]', '', text)
        # Remove articles for answer comparison
        text = re.sub(r'\b(a|an|the)\b', '', text)
        return text.strip()
    
    def _grade_numeric(self, student: str, correct: str) -> Optional[dict]:
        """Grade numeric answers with tolerance"""
        try:
            # Extract numbers from strings
            student_num = self._extract_number(student)
            correct_num = self._extract_number(correct)
            
            if student_num is None or correct_num is None:
                return None
            
            # Check exact match first
            if student_num == correct_num:
                return {
                    "is_correct": True,
                    "is_partial": False,
                    "score": 1.0,
                    "feedback": "Correct!"
                }
            
            # Calculate relative tolerance (1% for most answers)
            tolerance = abs(correct_num * 0.01) if correct_num != 0 else 0.01
            
            if abs(student_num - correct_num) <= tolerance:
                return {
                    "is_correct": True,
                    "is_partial": False,
                    "score": 1.0,
                    "feedback": "Correct! (Within acceptable tolerance)"
                }
            
            # Check if close (within 10%)
            if abs(student_num - correct_num) <= abs(correct_num * 0.1):
                return {
                    "is_correct": False,
                    "is_partial": True,
                    "score": 0.5,
                    "feedback": f"Close! Your answer is approximately correct but not precise enough."
                }
            
            return None  # Let other layers handle
        except Exception:
            return None
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract a number from text"""
        # Remove common units and symbols
        text = re.sub(r'[%$€£°]', '', text)
        # Handle fractions
        fraction_match = re.search(r'(\d+)\s*/\s*(\d+)', text)
        if fraction_match:
            return float(fraction_match.group(1)) / float(fraction_match.group(2))
        # Handle decimals
        number_match = re.search(r'-?\d+\.?\d*', text.replace(',', ''))
        if number_match:
            return float(number_match.group())
        return None
    
    def _grade_multiple_choice(self, student: str, correct: str, options: list) -> dict:
        """Grade multiple choice answers"""
        student_normalized = student.upper().strip()
        correct_normalized = correct.upper().strip()
        
        # Handle letter answers (A, B, C, D)
        if student_normalized in ['A', 'B', 'C', 'D']:
            if student_normalized == correct_normalized:
                return {
                    "is_correct": True,
                    "is_partial": False,
                    "score": 1.0,
                    "feedback": "Correct!"
                }
        
        # Handle full text answers
        if options and self._normalize(student) == self._normalize(correct):
            return {
                "is_correct": True,
                "is_partial": False,
                "score": 1.0,
                "feedback": "Correct!"
            }
        
        # Check if answer matches any option text
        if options:
            for i, option in enumerate(options):
                if self._normalize(student) == self._normalize(option):
                    expected_letter = chr(65 + i)  # A, B, C, D
                    if expected_letter == correct_normalized:
                        return {
                            "is_correct": True,
                            "is_partial": False,
                            "score": 1.0,
                            "feedback": "Correct!"
                        }
        
        return {
            "is_correct": False,
            "is_partial": False,
            "score": 0.0,
            "feedback": "That's not the correct answer. Review the options carefully."
        }
    
    def _check_partial_match(self, student: str, correct: str) -> dict:
        """Check for partial matches in free text"""
        student_words = set(self._normalize(student).split())
        correct_words = set(self._normalize(correct).split())
        
        if not correct_words:
            return {"is_partial": False}
        
        # Calculate overlap
        overlap = len(student_words & correct_words) / len(correct_words)
        
        if overlap >= 0.7:
            return {
                "is_correct": False,
                "is_partial": True,
                "score": overlap * 0.8,  # Cap partial at 80%
                "feedback": "You're on the right track! Your answer contains key concepts but isn't quite complete."
            }
        elif overlap >= 0.4:
            return {
                "is_correct": False,
                "is_partial": True,
                "score": overlap * 0.5,
                "feedback": "You have some of the right ideas. Let me help you understand better."
            }
        
        return {"is_partial": False}
    
    async def _grade_with_ai(self, question: Question, student_answer: str) -> Optional[dict]:
        """Use AI for semantic grading of complex answers"""
        if not self.anthropic_client:
            return None
        
        try:
            prompt = f"""You are grading a student's answer. Be encouraging but accurate.

Question: {question.question_text}
Correct Answer: {question.correct_answer}
Student's Answer: {student_answer}

Evaluate the student's answer and respond in this exact JSON format:
{{
    "is_correct": true/false,
    "is_partial": true/false,
    "score": 0.0-1.0,
    "feedback": "encouraging feedback message"
}}

Consider:
- Semantic equivalence (different wording, same meaning = correct)
- Partial credit for partially correct answers
- Be encouraging even when wrong
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cheap for grading
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            import json
            result_text = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "is_correct": result.get("is_correct", False),
                    "is_partial": result.get("is_partial", False),
                    "score": float(result.get("score", 0)),
                    "feedback": result.get("feedback", "Let me check that answer...")
                }
        except Exception as e:
            print(f"AI grading error: {e}")
            return None
        
        return None
    
    def _generate_feedback(self, question: Question, student: str, correct: str) -> str:
        """Generate helpful feedback for wrong answers"""
        feedbacks = [
            "Not quite right. Let's think about this differently.",
            "That's not the answer I was looking for. Would you like a hint?",
            "Keep trying! Learning happens through practice.",
            "Almost there! Let me explain the concept.",
            "Good attempt! Here's what to consider..."
        ]
        import random
        return random.choice(feedbacks)
