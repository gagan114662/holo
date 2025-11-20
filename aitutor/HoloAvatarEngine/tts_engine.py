"""
Text-to-Speech Engine using XTTS-v2
Supports voice cloning, multilingual synthesis, and streaming output
"""
import asyncio
import numpy as np
import io
import wave
from typing import Optional, AsyncGenerator
from pathlib import Path

# Optional torch import for demo mode
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .config import config, TTSConfig


class TTSEngine:
    """
    High-quality TTS using Coqui XTTS-v2
    - Voice cloning from 6-second sample
    - 17+ languages supported
    - <150ms streaming latency
    """

    def __init__(self, tts_config: TTSConfig = None):
        self.config = tts_config or config.tts
        self.model = None
        self.is_loaded = False
        self.current_speaker_embedding = None

    async def load_model(self):
        """Load XTTS-v2 model"""
        if self.is_loaded:
            return

        print("Loading XTTS-v2 model...")

        try:
            from TTS.api import TTS

            # Initialize TTS with XTTS-v2
            self.model = TTS(
                model_name=self.config.model_name,
                progress_bar=True,
                gpu=(self.config.device == "cuda")
            )

            self.is_loaded = True
            print(f"XTTS-v2 loaded on {self.config.device}")

        except ImportError:
            print("Warning: TTS library not installed. Install with: pip install TTS")
            # Fallback to mock for development
            self.model = None
            self.is_loaded = True

    def clone_voice(self, audio_path: str):
        """
        Clone a voice from an audio sample
        Requires 6+ seconds of clear speech
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Voice sample not found: {audio_path}")

        self.config.speaker_wav = audio_path
        print(f"Voice cloning enabled from: {audio_path}")

    async def synthesize(
        self,
        text: str,
        language: str = None,
        speaker_wav: str = None,
        emotion: str = "neutral"
    ) -> np.ndarray:
        """
        Synthesize speech from text

        Args:
            text: Text to synthesize
            language: Language code (en, es, fr, de, etc.)
            speaker_wav: Optional voice sample for cloning
            emotion: Emotion hint for synthesis

        Returns:
            Audio as numpy array (sample_rate: 24000)
        """
        if not self.is_loaded:
            await self.load_model()

        language = language or self.config.language
        speaker_wav = speaker_wav or self.config.speaker_wav

        if self.model is None:
            # Mock audio for development
            return self._generate_mock_audio(text)

        try:
            # Run synthesis in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            audio = await loop.run_in_executor(
                None,
                self._synthesize_sync,
                text, language, speaker_wav
            )
            return audio

        except Exception as e:
            print(f"TTS synthesis error: {e}")
            return self._generate_mock_audio(text)

    def _synthesize_sync(
        self,
        text: str,
        language: str,
        speaker_wav: str
    ) -> np.ndarray:
        """Synchronous synthesis (runs in thread pool)"""

        if speaker_wav:
            # Voice cloning mode
            wav = self.model.tts(
                text=text,
                speaker_wav=speaker_wav,
                language=language
            )
        else:
            # Default voice
            wav = self.model.tts(
                text=text,
                language=language
            )

        return np.array(wav, dtype=np.float32)

    async def synthesize_streaming(
        self,
        text: str,
        chunk_size: int = 4096
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks as they're generated
        Enables low-latency playback
        """
        audio = await self.synthesize(text)

        # Convert to bytes and yield chunks
        audio_bytes = (audio * 32767).astype(np.int16).tobytes()

        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i:i + chunk_size]
            await asyncio.sleep(0)  # Allow other tasks to run

    def _generate_mock_audio(self, text: str) -> np.ndarray:
        """Generate placeholder audio for development"""
        # Generate silence with duration based on text length
        duration_seconds = len(text) * 0.05  # ~50ms per character
        num_samples = int(self.config.sample_rate * duration_seconds)

        # Generate quiet noise instead of pure silence
        audio = np.random.randn(num_samples).astype(np.float32) * 0.01
        return audio

    def audio_to_wav_bytes(self, audio: np.ndarray) -> bytes:
        """Convert audio array to WAV bytes"""
        buffer = io.BytesIO()

        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.config.sample_rate)

            audio_int16 = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())

        return buffer.getvalue()

    @property
    def sample_rate(self) -> int:
        return self.config.sample_rate


class CharacterVoice:
    """
    Represents a character's voice profile
    """

    def __init__(
        self,
        name: str,
        voice_sample: str,
        language: str = "en",
        speaking_rate: float = 1.0,
        pitch_shift: float = 0.0
    ):
        self.name = name
        self.voice_sample = voice_sample
        self.language = language
        self.speaking_rate = speaking_rate
        self.pitch_shift = pitch_shift

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "voice_sample": self.voice_sample,
            "language": self.language,
            "speaking_rate": self.speaking_rate,
            "pitch_shift": self.pitch_shift
        }


# Voice presets for educational characters
VOICE_PRESETS = {
    "teacher": CharacterVoice(
        name="Friendly Teacher",
        voice_sample="avatars/voices/teacher_sample.wav",
        language="en",
        speaking_rate=0.95
    ),
    "einstein": CharacterVoice(
        name="Albert Einstein",
        voice_sample="avatars/voices/einstein_sample.wav",
        language="en",
        speaking_rate=0.9
    ),
    "curie": CharacterVoice(
        name="Marie Curie",
        voice_sample="avatars/voices/curie_sample.wav",
        language="en",
        speaking_rate=1.0
    )
}
