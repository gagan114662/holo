"""
Avatar Manager - Main orchestration for HoloAvatar system
Coordinates TTS, talking head, and expressions
"""
import asyncio
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from .config import config, load_config
from .tts_engine import TTSEngine, VOICE_PRESETS
from .talking_head import TalkingHeadEngine, LipSyncProcessor, AVATAR_PRESETS
from .expression_controller import ExpressionController, Expression


@dataclass
class Character:
    """Represents an avatar character"""
    id: str
    name: str
    description: str
    portrait_path: str
    voice_sample_path: str
    personality: dict
    subjects: list
    grade_levels: list


class AvatarManager:
    """
    Main orchestrator for HoloAvatar system

    Coordinates:
    - Text-to-speech generation
    - Talking head animation
    - Expression control
    - Character management
    """

    def __init__(self):
        self.config = load_config()

        # Components
        self.tts_engine = TTSEngine()
        self.talking_head = TalkingHeadEngine()
        self.expression_controller = ExpressionController()
        self.lip_sync = LipSyncProcessor()

        # State
        self.current_character: Optional[Character] = None
        self.is_speaking = False
        self.is_initialized = False

        # Frame generation
        self._frame_task: Optional[asyncio.Task] = None
        self._audio_queue: asyncio.Queue = asyncio.Queue()
        self._should_run = False

        # Callbacks
        self.on_frame_ready = None
        self.on_audio_ready = None
        self.on_state_change = None

        # Performance metrics
        self.metrics = {
            "frames_generated": 0,
            "audio_generated": 0,
            "avg_frame_time_ms": 0
        }

    async def initialize(self):
        """Initialize all components"""
        if self.is_initialized:
            return

        print("Initializing HoloAvatar system...")

        # Load models
        await self.tts_engine.load_model()
        await self.talking_head.load_model()

        # Load default character
        await self.load_character(self.config.default_character)

        self.is_initialized = True
        print("HoloAvatar system ready!")

    async def load_character(self, character_id: str):
        """
        Load a character by ID

        Args:
            character_id: Character identifier (e.g., "teacher", "einstein")
        """
        # Get character definition
        if character_id not in AVATAR_PRESETS:
            raise ValueError(f"Unknown character: {character_id}")

        preset = AVATAR_PRESETS[character_id]
        voice_preset = VOICE_PRESETS.get(character_id)

        self.current_character = Character(
            id=character_id,
            name=preset["name"],
            description=preset["description"],
            portrait_path=preset["image"],
            voice_sample_path=voice_preset.voice_sample if voice_preset else "",
            personality={},
            subjects=[],
            grade_levels=[]
        )

        # Configure talking head with portrait
        portrait_path = Path(self.config.avatars_dir) / character_id / "portrait.png"
        if portrait_path.exists():
            self.talking_head.set_source_image(str(portrait_path))
        else:
            # Use placeholder
            print(f"Portrait not found at {portrait_path}, using placeholder")

        # Configure TTS with voice sample
        if voice_preset and Path(voice_preset.voice_sample).exists():
            self.tts_engine.clone_voice(voice_preset.voice_sample)

        print(f"Character loaded: {preset['name']}")

        if self.on_state_change:
            await self.on_state_change("character_loaded", {"character": character_id})

    async def speak(
        self,
        text: str,
        emotion: str = "neutral",
        language: str = None
    ):
        """
        Make the avatar speak

        Args:
            text: Text to speak
            emotion: Emotion for expression
            language: Language code
        """
        if not self.is_initialized:
            await self.initialize()

        self.is_speaking = True

        # Set expression based on emotion
        try:
            expr = Expression(emotion)
        except ValueError:
            expr = Expression.NEUTRAL

        self.expression_controller.set_expression(expr, 0.8)

        # Generate audio
        audio = await self.tts_engine.synthesize(text, language)

        # Generate lip sync data
        visemes = self.lip_sync.audio_to_visemes(
            audio, self.tts_engine.sample_rate
        )

        # Queue audio for playback
        await self._audio_queue.put({
            "audio": audio,
            "visemes": visemes,
            "text": text
        })

        # Send audio to client
        if self.on_audio_ready:
            audio_bytes = self.tts_engine.audio_to_wav_bytes(audio)
            await self.on_audio_ready(audio_bytes)

        self.metrics["audio_generated"] += 1
        self.is_speaking = False

    async def start_frame_generation(self):
        """Start continuous frame generation loop"""
        self._should_run = True
        self._frame_task = asyncio.create_task(self._frame_loop())
        print("Frame generation started")

    async def stop_frame_generation(self):
        """Stop frame generation loop"""
        self._should_run = False
        if self._frame_task:
            self._frame_task.cancel()
            try:
                await self._frame_task
            except asyncio.CancelledError:
                pass
        print("Frame generation stopped")

    async def _frame_loop(self):
        """Main frame generation loop"""
        target_interval = 1.0 / self.config.target_fps

        while self._should_run:
            start_time = time.time()

            # Get current expression
            expr_params = self.expression_controller.get_expression_params()

            # Get audio chunk if speaking
            audio_chunk = None
            if not self._audio_queue.empty():
                try:
                    audio_data = self._audio_queue.get_nowait()
                    audio_chunk = audio_data.get("audio")
                except asyncio.QueueEmpty:
                    pass

            # Generate frame
            try:
                frame = await self.talking_head.generate_frame(
                    audio_chunk=audio_chunk,
                    expression=expr_params["expression"],
                    intensity=expr_params["intensity"]
                )

                # Convert to base64
                frame_base64 = self.talking_head.frame_to_base64(frame)

                # Send to client
                if self.on_frame_ready:
                    await self.on_frame_ready({
                        "frame": frame_base64,
                        "expression": expr_params["expression"],
                        "speaking": self.is_speaking,
                        "timestamp": time.time()
                    })

                self.metrics["frames_generated"] += 1

            except Exception as e:
                print(f"Frame generation error: {e}")

            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, target_interval - elapsed)
            await asyncio.sleep(sleep_time)

            # Update metrics
            self.metrics["avg_frame_time_ms"] = self.talking_head.average_frame_time_ms

    async def trigger_expression(self, event_name: str, data: dict = None):
        """Trigger an expression based on event"""
        self.expression_controller.trigger_event(event_name)

        if self.on_state_change:
            await self.on_state_change("expression_changed", {
                "event": event_name,
                "expression": self.expression_controller.current_state.expression.value
            })

    async def process_dash_event(self, event_type: str, event_data: dict):
        """Process event from DASH adaptive learning system"""
        self.expression_controller.process_dash_event(event_type, event_data)

    def get_state(self) -> dict:
        """Get current avatar state"""
        return {
            "character": self.current_character.id if self.current_character else None,
            "character_name": self.current_character.name if self.current_character else None,
            "is_speaking": self.is_speaking,
            "expression": self.expression_controller.current_state.expression.value,
            "is_initialized": self.is_initialized,
            "metrics": self.metrics
        }

    def get_available_characters(self) -> list:
        """Get list of available characters"""
        return [
            {
                "id": char_id,
                "name": preset["name"],
                "description": preset["description"]
            }
            for char_id, preset in AVATAR_PRESETS.items()
        ]


# Singleton instance
_avatar_manager: Optional[AvatarManager] = None


def get_avatar_manager() -> AvatarManager:
    """Get the global avatar manager instance"""
    global _avatar_manager
    if _avatar_manager is None:
        _avatar_manager = AvatarManager()
    return _avatar_manager
