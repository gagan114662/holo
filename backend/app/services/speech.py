"""
Speech Services
Handles speech-to-text (Whisper) and text-to-speech for multilingual support.
Supports 100+ languages - key differentiator over 2wai's 40 languages.
"""
import asyncio
import aiofiles
import base64
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal

logger = logging.getLogger(__name__)

# Supported languages (Whisper supports 99 languages)
SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ru": "Russian",
    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
    "hi": "Hindi", "bn": "Bengali", "pa": "Punjabi", "ta": "Tamil",
    "te": "Telugu", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "th": "Thai", "vi": "Vietnamese", "id": "Indonesian",
    "ms": "Malay", "fil": "Filipino", "tr": "Turkish", "pl": "Polish",
    "uk": "Ukrainian", "cs": "Czech", "ro": "Romanian", "hu": "Hungarian",
    "el": "Greek", "he": "Hebrew", "sv": "Swedish", "da": "Danish",
    "no": "Norwegian", "fi": "Finnish", "ca": "Catalan", "hr": "Croatian",
    "sk": "Slovak", "bg": "Bulgarian", "lt": "Lithuanian", "lv": "Latvian",
    "et": "Estonian", "sl": "Slovenian", "sr": "Serbian", "sw": "Swahili",
    "af": "Afrikaans", "cy": "Welsh", "ga": "Irish", "eu": "Basque",
    # ... and many more (Whisper supports 99 total)
}

# Edge TTS voices by language
EDGE_TTS_VOICES = {
    "en": "en-US-GuyNeural",
    "en-gb": "en-GB-RyanNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "it": "it-IT-DiegoNeural",
    "pt": "pt-BR-AntonioNeural",
    "nl": "nl-NL-MaartenNeural",
    "ru": "ru-RU-DmitryNeural",
    "zh": "zh-CN-YunxiNeural",
    "ja": "ja-JP-KeitaNeural",
    "ko": "ko-KR-InJoonNeural",
    "ar": "ar-SA-HamedNeural",
    "hi": "hi-IN-MadhurNeural",
    "tr": "tr-TR-AhmetNeural",
    "pl": "pl-PL-MarekNeural",
    "vi": "vi-VN-NamMinhNeural",
    "th": "th-TH-NiwatNeural",
    "id": "id-ID-ArdiNeural",
}


@dataclass
class TranscriptionResult:
    """Result of speech-to-text transcription"""
    text: str
    language: str
    confidence: float
    segments: list[dict]
    duration: float


@dataclass
class SynthesisResult:
    """Result of text-to-speech synthesis"""
    audio_path: str
    duration: float
    voice_id: str
    language: str


class SpeechService:
    """
    Unified speech service supporting:
    - Speech-to-Text via Whisper (100+ languages)
    - Text-to-Speech via Edge TTS (40+ languages)
    - Real-time translation
    """

    def __init__(self):
        self.whisper_model = None
        self.model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        self._whisper_lock = asyncio.Lock()
        self._init_task = None

    async def _ensure_whisper_loaded(self):
        """Lazy-load Whisper model on first use"""
        if self.whisper_model is not None:
            return

        async with self._whisper_lock:
            if self.whisper_model is not None:
                return

            # Try faster-whisper first (faster inference)
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Loading faster-whisper model: {self.model_size}")

                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self.whisper_model = await loop.run_in_executor(
                    None,
                    lambda: WhisperModel(
                        self.model_size,
                        device="cpu",  # Use "cuda" if GPU available
                        compute_type="int8"
                    )
                )
                self._whisper_type = "faster"
                logger.info("faster-whisper loaded successfully")
                return
            except ImportError:
                logger.warning("faster-whisper not available, trying openai-whisper")
            except Exception as e:
                logger.error(f"Failed to load faster-whisper: {e}")

            # Fallback to openai-whisper
            try:
                import whisper
                logger.info(f"Loading openai-whisper model: {self.model_size}")

                loop = asyncio.get_event_loop()
                self.whisper_model = await loop.run_in_executor(
                    None,
                    lambda: whisper.load_model(self.model_size)
                )
                self._whisper_type = "openai"
                logger.info("openai-whisper loaded successfully")
            except ImportError:
                logger.error("No Whisper implementation available")
                self.whisper_model = None
            except Exception as e:
                logger.error(f"Failed to load whisper: {e}")
                self.whisper_model = None

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        task: Literal["transcribe", "translate"] = "transcribe"
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe audio to text using Whisper.

        Args:
            audio_data: Raw audio bytes (WAV, MP3, etc.)
            language: Optional language code (auto-detected if not provided)
            task: "transcribe" for same-language, "translate" for English translation

        Returns:
            TranscriptionResult or None if failed
        """
        await self._ensure_whisper_loaded()

        if self.whisper_model is None:
            logger.error("Whisper not available")
            return None

        # Save audio to temp file (Whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            audio_path = f.name

        try:
            loop = asyncio.get_event_loop()

            if self._whisper_type == "faster":
                # faster-whisper API
                segments, info = await loop.run_in_executor(
                    None,
                    lambda: self.whisper_model.transcribe(
                        audio_path,
                        language=language,
                        task=task,
                        beam_size=5
                    )
                )

                # Collect segments
                segment_list = []
                full_text = []
                for segment in segments:
                    segment_list.append({
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text
                    })
                    full_text.append(segment.text)

                return TranscriptionResult(
                    text=" ".join(full_text).strip(),
                    language=info.language,
                    confidence=info.language_probability,
                    segments=segment_list,
                    duration=info.duration
                )

            else:
                # openai-whisper API
                result = await loop.run_in_executor(
                    None,
                    lambda: self.whisper_model.transcribe(
                        audio_path,
                        language=language,
                        task=task
                    )
                )

                segments = [
                    {"start": s["start"], "end": s["end"], "text": s["text"]}
                    for s in result.get("segments", [])
                ]

                return TranscriptionResult(
                    text=result["text"].strip(),
                    language=result.get("language", "en"),
                    confidence=1.0,  # openai-whisper doesn't provide confidence
                    segments=segments,
                    duration=segments[-1]["end"] if segments else 0
                )

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

        finally:
            # Clean up temp file
            try:
                os.unlink(audio_path)
            except Exception:
                pass

    async def synthesize(
        self,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None
    ) -> Optional[SynthesisResult]:
        """
        Convert text to speech using Edge TTS.

        Args:
            text: Text to synthesize
            language: Language code
            voice_id: Optional specific voice ID

        Returns:
            SynthesisResult with path to audio file
        """
        if not voice_id:
            voice_id = EDGE_TTS_VOICES.get(language, EDGE_TTS_VOICES["en"])

        output_path = f"/tmp/holotutor/tts_{uuid.uuid4().hex[:8]}.mp3"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # Use edge-tts CLI
            proc = await asyncio.create_subprocess_exec(
                "edge-tts",
                "--text", text,
                "--voice", voice_id,
                "--write-media", output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0 and os.path.exists(output_path):
                # Get duration (rough estimate: ~150 words per minute)
                word_count = len(text.split())
                duration = word_count / 2.5  # ~150 wpm

                return SynthesisResult(
                    audio_path=output_path,
                    duration=duration,
                    voice_id=voice_id,
                    language=language
                )
            else:
                logger.error(f"Edge TTS failed: {stderr.decode()}")

        except FileNotFoundError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")

        return None

    async def translate_audio(
        self,
        audio_data: bytes,
        target_language: str = "en"
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe and translate audio to target language.
        Whisper has built-in translation to English.

        Args:
            audio_data: Raw audio bytes
            target_language: Target language (currently only "en" supported by Whisper)

        Returns:
            TranscriptionResult with translated text
        """
        if target_language != "en":
            # For non-English targets, would need separate translation service
            logger.warning(f"Translation to {target_language} not yet supported, using English")

        return await self.transcribe(audio_data, task="translate")

    def get_supported_languages(self) -> dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return SUPPORTED_LANGUAGES.copy()

    def get_tts_voices(self) -> dict[str, str]:
        """Get dictionary of available TTS voices by language"""
        return EDGE_TTS_VOICES.copy()


# Global service instance
speech_service = SpeechService()
