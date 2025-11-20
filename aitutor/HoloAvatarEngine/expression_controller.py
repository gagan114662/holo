"""
Expression Controller
Maps learning context to avatar expressions and reactions
"""
import asyncio
import time
from typing import Dict, Optional, Callable
from enum import Enum
from dataclasses import dataclass

from .config import config, ExpressionConfig


class Expression(Enum):
    """Available avatar expressions"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    THINKING = "thinking"
    ENCOURAGING = "encouraging"
    CONCERNED = "concerned"
    EXCITED = "excited"
    PROUD = "proud"
    CURIOUS = "curious"
    EXPLAINING = "explaining"
    LISTENING = "listening"


@dataclass
class ExpressionState:
    """Current expression state"""
    expression: Expression
    intensity: float
    start_time: float
    duration: float = 0  # 0 means indefinite
    blend_from: Optional[Expression] = None
    blend_progress: float = 1.0


class ExpressionController:
    """
    Controls avatar expressions based on learning context

    Maps DASH system events to appropriate expressions
    and handles smooth transitions between expressions.
    """

    def __init__(self, expr_config: ExpressionConfig = None):
        self.config = expr_config or config.expressions
        self.current_state = ExpressionState(
            expression=Expression.NEUTRAL,
            intensity=0.5,
            start_time=time.time()
        )

        # Event to expression mapping
        self.event_mappings: Dict[str, ExpressionState] = {}
        self._setup_default_mappings()

        # Callbacks
        self.on_expression_change: Optional[Callable] = None

        # Idle animation state
        self._idle_timer = 0
        self._last_update = time.time()

    def _setup_default_mappings(self):
        """Set up default event-to-expression mappings"""

        # Student performance events
        self.map_event("student_correct_fast", Expression.EXCITED, 0.9, 2.0)
        self.map_event("student_correct", Expression.HAPPY, 0.8, 2.0)
        self.map_event("student_correct_slow", Expression.ENCOURAGING, 0.7, 2.0)
        self.map_event("student_incorrect", Expression.THINKING, 0.6, 1.5)
        self.map_event("student_struggling", Expression.CONCERNED, 0.7, 3.0)
        self.map_event("student_mastery", Expression.PROUD, 0.9, 3.0)
        self.map_event("student_improving", Expression.HAPPY, 0.8, 2.5)

        # Teaching events
        self.map_event("explaining_concept", Expression.EXPLAINING, 0.7, 0)
        self.map_event("asking_question", Expression.CURIOUS, 0.6, 0)
        self.map_event("waiting_response", Expression.LISTENING, 0.5, 0)
        self.map_event("giving_hint", Expression.ENCOURAGING, 0.7, 2.0)

        # Interaction events
        self.map_event("greeting", Expression.HAPPY, 0.8, 2.0)
        self.map_event("farewell", Expression.HAPPY, 0.7, 2.0)
        self.map_event("encouragement", Expression.ENCOURAGING, 0.8, 2.5)

    def map_event(
        self,
        event_name: str,
        expression: Expression,
        intensity: float,
        duration: float
    ):
        """Map an event to an expression"""
        self.event_mappings[event_name] = ExpressionState(
            expression=expression,
            intensity=intensity,
            start_time=0,  # Will be set on trigger
            duration=duration
        )

    def trigger_event(self, event_name: str, intensity_modifier: float = 1.0):
        """
        Trigger an expression change based on event

        Args:
            event_name: Name of the event
            intensity_modifier: Multiply base intensity (0.0 - 2.0)
        """
        if event_name not in self.event_mappings:
            print(f"Unknown event: {event_name}")
            return

        if not self.config.auto_react:
            return

        mapping = self.event_mappings[event_name]

        new_state = ExpressionState(
            expression=mapping.expression,
            intensity=min(mapping.intensity * intensity_modifier, 1.0),
            start_time=time.time(),
            duration=mapping.duration,
            blend_from=self.current_state.expression,
            blend_progress=0.0
        )

        self._transition_to(new_state)

    def set_expression(
        self,
        expression: Expression,
        intensity: float = 0.7,
        duration: float = 0
    ):
        """Manually set expression"""
        new_state = ExpressionState(
            expression=expression,
            intensity=intensity,
            start_time=time.time(),
            duration=duration,
            blend_from=self.current_state.expression,
            blend_progress=0.0
        )

        self._transition_to(new_state)

    def _transition_to(self, new_state: ExpressionState):
        """Transition to new expression state"""
        self.current_state = new_state

        if self.on_expression_change:
            self.on_expression_change(new_state)

    def update(self) -> ExpressionState:
        """
        Update expression state (call every frame)

        Returns current expression state with updated blend progress
        """
        current_time = time.time()
        dt = current_time - self._last_update
        self._last_update = current_time

        # Update blend progress
        if self.current_state.blend_progress < 1.0:
            blend_speed = 1000 / self.config.blend_duration_ms
            self.current_state.blend_progress = min(
                self.current_state.blend_progress + dt * blend_speed,
                1.0
            )

        # Check if duration expired
        if self.current_state.duration > 0:
            elapsed = current_time - self.current_state.start_time
            if elapsed >= self.current_state.duration:
                # Return to neutral
                self.set_expression(Expression.NEUTRAL, 0.5)

        # Idle animations
        if self.config.idle_animations:
            self._update_idle(dt)

        return self.current_state

    def _update_idle(self, dt: float):
        """Update idle animation state"""
        self._idle_timer += dt

        # Subtle expression changes during idle
        if self._idle_timer > 5.0 and self.current_state.expression == Expression.NEUTRAL:
            self._idle_timer = 0
            # Small intensity fluctuation
            self.current_state.intensity = 0.5 + (time.time() % 1) * 0.1

    def get_expression_params(self) -> dict:
        """Get current expression parameters for rendering"""
        state = self.update()

        return {
            "expression": state.expression.value,
            "intensity": state.intensity,
            "blend_from": state.blend_from.value if state.blend_from else None,
            "blend_progress": state.blend_progress
        }

    def process_dash_event(self, event_type: str, event_data: dict):
        """
        Process events from DASH adaptive learning system

        Args:
            event_type: Type of learning event
            event_data: Additional event data
        """
        # Map DASH events to expression events
        if event_type == "question_answered":
            is_correct = event_data.get("is_correct", False)
            response_time = event_data.get("response_time", 10)
            attempt_count = event_data.get("attempt_count", 1)

            if is_correct:
                if response_time < 5:
                    self.trigger_event("student_correct_fast")
                elif attempt_count == 1:
                    self.trigger_event("student_correct")
                else:
                    self.trigger_event("student_correct_slow")
            else:
                if attempt_count > 2:
                    self.trigger_event("student_struggling")
                else:
                    self.trigger_event("student_incorrect")

        elif event_type == "skill_mastered":
            self.trigger_event("student_mastery")

        elif event_type == "skill_improved":
            self.trigger_event("student_improving")

        elif event_type == "question_displayed":
            self.trigger_event("asking_question")

        elif event_type == "hint_given":
            self.trigger_event("giving_hint")

        elif event_type == "explanation_started":
            self.trigger_event("explaining_concept")


# Expression blending utilities
def blend_expressions(
    expr1: str,
    expr2: str,
    progress: float
) -> dict:
    """
    Blend between two expressions

    Args:
        expr1: Source expression name
        expr2: Target expression name
        progress: Blend progress (0.0 = expr1, 1.0 = expr2)

    Returns:
        Blended expression parameters
    """
    # Define expression parameter vectors (simplified)
    expression_params = {
        "neutral": {"mouth_open": 0.0, "brow_up": 0.0, "smile": 0.0},
        "happy": {"mouth_open": 0.2, "brow_up": 0.3, "smile": 0.8},
        "thinking": {"mouth_open": 0.1, "brow_up": -0.3, "smile": 0.0},
        "encouraging": {"mouth_open": 0.3, "brow_up": 0.2, "smile": 0.6},
        "concerned": {"mouth_open": 0.1, "brow_up": -0.2, "smile": -0.3},
        "excited": {"mouth_open": 0.5, "brow_up": 0.5, "smile": 0.9},
        "proud": {"mouth_open": 0.3, "brow_up": 0.3, "smile": 0.7},
        "curious": {"mouth_open": 0.2, "brow_up": 0.4, "smile": 0.2},
        "explaining": {"mouth_open": 0.4, "brow_up": 0.1, "smile": 0.3},
        "listening": {"mouth_open": 0.0, "brow_up": 0.2, "smile": 0.2},
    }

    params1 = expression_params.get(expr1, expression_params["neutral"])
    params2 = expression_params.get(expr2, expression_params["neutral"])

    # Linear interpolation
    blended = {}
    for key in params1:
        blended[key] = params1[key] * (1 - progress) + params2[key] * progress

    return blended
