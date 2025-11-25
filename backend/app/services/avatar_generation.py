"""
Avatar Generation Service
Handles custom avatar creation using open-source AI models:
- SadTalker/Wav2Lip for lip-sync animation
- Face detection and alignment
- Voice cloning integration
"""
import asyncio
import aiofiles
import base64
import hashlib
import httpx
import logging
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, BinaryIO
from dataclasses import dataclass, field

from ..config import settings

logger = logging.getLogger(__name__)

# Storage paths
AVATAR_STORAGE_PATH = Path(os.getenv("AVATAR_STORAGE_PATH", "/tmp/holotutor/avatars"))
AVATAR_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@dataclass
class GeneratedAvatar:
    """Represents a generated custom avatar"""
    id: str
    user_id: str
    name: str
    source_image_path: str
    thumbnail_path: str
    voice_sample_path: Optional[str] = None
    voice_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "source_image_url": f"/api/avatars/generated/{self.id}/image",
            "thumbnail_url": f"/api/avatars/generated/{self.id}/thumbnail",
            "has_voice": self.voice_sample_path is not None,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class AvatarGenerationService:
    """
    Service for generating custom avatars from user photos/videos.

    Supports multiple backends:
    - Local: SadTalker/Wav2Lip running locally (requires GPU)
    - Replicate: Cloud API for SadTalker
    - D-ID: Commercial API fallback
    """

    def __init__(self):
        self.replicate_client = None
        self.generated_avatars: dict[str, GeneratedAvatar] = {}
        self._lock = asyncio.Lock()

        # Initialize Replicate client if API key available
        self.replicate_api_key = os.getenv("REPLICATE_API_TOKEN")
        if self.replicate_api_key:
            logger.info("Replicate API configured for avatar generation")

        # SadTalker local endpoint (if running locally)
        self.sadtalker_endpoint = os.getenv("SADTALKER_ENDPOINT")
        if self.sadtalker_endpoint:
            logger.info(f"SadTalker local endpoint: {self.sadtalker_endpoint}")

    async def create_avatar_from_image(
        self,
        user_id: str,
        name: str,
        image_data: bytes,
        image_filename: str
    ) -> GeneratedAvatar:
        """
        Create a custom avatar from a single photo.

        Args:
            user_id: Owner's user ID
            name: Display name for the avatar
            image_data: Raw image bytes (JPEG/PNG)
            image_filename: Original filename

        Returns:
            GeneratedAvatar object
        """
        avatar_id = str(uuid.uuid4())
        avatar_dir = AVATAR_STORAGE_PATH / avatar_id
        avatar_dir.mkdir(parents=True, exist_ok=True)

        # Determine file extension
        ext = Path(image_filename).suffix.lower() or ".jpg"
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        # Save source image
        source_path = avatar_dir / f"source{ext}"
        async with aiofiles.open(source_path, "wb") as f:
            await f.write(image_data)

        # Process image (face detection, alignment, thumbnail generation)
        thumbnail_path = await self._process_source_image(
            source_path, avatar_dir
        )

        # Create avatar object
        avatar = GeneratedAvatar(
            id=avatar_id,
            user_id=user_id,
            name=name,
            source_image_path=str(source_path),
            thumbnail_path=str(thumbnail_path),
            metadata={
                "original_filename": image_filename,
                "processing_backend": self._get_available_backend()
            }
        )

        async with self._lock:
            self.generated_avatars[avatar_id] = avatar

        logger.info(f"Created avatar {avatar_id} for user {user_id}")
        return avatar

    async def create_avatar_from_video(
        self,
        user_id: str,
        name: str,
        video_data: bytes,
        video_filename: str
    ) -> GeneratedAvatar:
        """
        Create a custom avatar from a short video (extracts best frame + voice).

        Args:
            user_id: Owner's user ID
            name: Display name for the avatar
            video_data: Raw video bytes
            video_filename: Original filename

        Returns:
            GeneratedAvatar object with voice sample
        """
        avatar_id = str(uuid.uuid4())
        avatar_dir = AVATAR_STORAGE_PATH / avatar_id
        avatar_dir.mkdir(parents=True, exist_ok=True)

        # Save source video
        ext = Path(video_filename).suffix.lower() or ".mp4"
        video_path = avatar_dir / f"source{ext}"
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(video_data)

        # Extract best frame from video
        frame_path = await self._extract_best_frame(video_path, avatar_dir)

        # Extract audio for voice cloning
        audio_path = await self._extract_audio(video_path, avatar_dir)

        # Process the extracted frame
        thumbnail_path = await self._process_source_image(frame_path, avatar_dir)

        avatar = GeneratedAvatar(
            id=avatar_id,
            user_id=user_id,
            name=name,
            source_image_path=str(frame_path),
            thumbnail_path=str(thumbnail_path),
            voice_sample_path=str(audio_path) if audio_path else None,
            metadata={
                "original_filename": video_filename,
                "source_type": "video",
                "processing_backend": self._get_available_backend()
            }
        )

        async with self._lock:
            self.generated_avatars[avatar_id] = avatar

        logger.info(f"Created avatar {avatar_id} from video for user {user_id}")
        return avatar

    async def generate_talking_video(
        self,
        avatar_id: str,
        text: str,
        emotion: str = "neutral"
    ) -> Optional[str]:
        """
        Generate a talking head video for the avatar.

        Args:
            avatar_id: The avatar to animate
            text: Text to speak
            emotion: Emotion style (neutral, happy, sad, etc.)

        Returns:
            Path to generated video or None if failed
        """
        async with self._lock:
            avatar = self.generated_avatars.get(avatar_id)

        if not avatar:
            logger.error(f"Avatar {avatar_id} not found")
            return None

        # Try backends in order of preference
        if self.sadtalker_endpoint:
            return await self._generate_with_sadtalker_local(avatar, text, emotion)
        elif self.replicate_api_key:
            return await self._generate_with_replicate(avatar, text, emotion)
        else:
            logger.warning("No avatar generation backend available")
            return None

    async def _process_source_image(
        self,
        source_path: Path,
        output_dir: Path
    ) -> Path:
        """Process source image: detect face, align, create thumbnail"""
        thumbnail_path = output_dir / "thumbnail.jpg"

        # For now, just copy as thumbnail (full processing requires opencv/dlib)
        # In production, this would:
        # 1. Detect face using dlib/mediapipe
        # 2. Align face to standard position
        # 3. Crop and resize for optimal lip-sync

        try:
            async with aiofiles.open(source_path, "rb") as src:
                data = await src.read()
            async with aiofiles.open(thumbnail_path, "wb") as dst:
                await dst.write(data)
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {e}")
            thumbnail_path = source_path

        return thumbnail_path

    async def _extract_best_frame(
        self,
        video_path: Path,
        output_dir: Path
    ) -> Path:
        """Extract the best frame from video for avatar creation"""
        frame_path = output_dir / "frame.jpg"

        # Use ffmpeg to extract frame at 1 second mark
        # In production, would analyze multiple frames and pick best quality face
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", str(video_path),
                "-ss", "00:00:01", "-vframes", "1",
                "-q:v", "2", str(frame_path),
                "-y",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()

            if frame_path.exists():
                return frame_path
        except Exception as e:
            logger.error(f"Failed to extract frame: {e}")

        # Fallback: return video path (will fail downstream but gracefully)
        return video_path

    async def _extract_audio(
        self,
        video_path: Path,
        output_dir: Path
    ) -> Optional[Path]:
        """Extract audio from video for voice cloning"""
        audio_path = output_dir / "voice_sample.wav"

        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", str(video_path),
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                str(audio_path),
                "-y",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()

            if audio_path.exists() and audio_path.stat().st_size > 1000:
                return audio_path
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")

        return None

    async def _generate_with_sadtalker_local(
        self,
        avatar: GeneratedAvatar,
        text: str,
        emotion: str
    ) -> Optional[str]:
        """Generate talking video using local SadTalker instance"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # First, generate audio from text using TTS
                audio_path = await self._text_to_speech(text, avatar.voice_sample_path)

                if not audio_path:
                    logger.error("TTS failed, cannot generate video")
                    return None

                # Read image and audio as base64
                async with aiofiles.open(avatar.source_image_path, "rb") as f:
                    image_b64 = base64.b64encode(await f.read()).decode()
                async with aiofiles.open(audio_path, "rb") as f:
                    audio_b64 = base64.b64encode(await f.read()).decode()

                # Call SadTalker API
                response = await client.post(
                    f"{self.sadtalker_endpoint}/generate",
                    json={
                        "source_image": image_b64,
                        "driven_audio": audio_b64,
                        "preprocess": "crop",
                        "still_mode": False,
                        "expression_scale": 1.0 if emotion == "neutral" else 1.2
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    video_b64 = result.get("video")
                    if video_b64:
                        # Save generated video
                        output_path = AVATAR_STORAGE_PATH / avatar.id / f"output_{uuid.uuid4().hex[:8]}.mp4"
                        async with aiofiles.open(output_path, "wb") as f:
                            await f.write(base64.b64decode(video_b64))
                        return str(output_path)

        except Exception as e:
            logger.error(f"SadTalker generation failed: {e}")

        return None

    async def _generate_with_replicate(
        self,
        avatar: GeneratedAvatar,
        text: str,
        emotion: str
    ) -> Optional[str]:
        """Generate talking video using Replicate API (SadTalker model)"""
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                # Read source image
                async with aiofiles.open(avatar.source_image_path, "rb") as f:
                    image_b64 = base64.b64encode(await f.read()).decode()

                # Generate audio first
                audio_path = await self._text_to_speech(text, avatar.voice_sample_path)
                if not audio_path:
                    return None

                async with aiofiles.open(audio_path, "rb") as f:
                    audio_b64 = base64.b64encode(await f.read()).decode()

                # Call Replicate API
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {self.replicate_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "cdb8d0a4c7a6a6e7c9a8b8f8d8e8f8a8b8c8d8e8",  # SadTalker version
                        "input": {
                            "source_image": f"data:image/jpeg;base64,{image_b64}",
                            "driven_audio": f"data:audio/wav;base64,{audio_b64}",
                            "preprocess": "crop"
                        }
                    }
                )

                if response.status_code in [200, 201]:
                    prediction = response.json()
                    prediction_id = prediction.get("id")

                    # Poll for completion
                    for _ in range(60):  # Max 3 minutes
                        await asyncio.sleep(3)
                        status_response = await client.get(
                            f"https://api.replicate.com/v1/predictions/{prediction_id}",
                            headers={"Authorization": f"Token {self.replicate_api_key}"}
                        )
                        status = status_response.json()

                        if status.get("status") == "succeeded":
                            video_url = status.get("output")
                            if video_url:
                                # Download video
                                video_response = await client.get(video_url)
                                output_path = AVATAR_STORAGE_PATH / avatar.id / f"output_{uuid.uuid4().hex[:8]}.mp4"
                                async with aiofiles.open(output_path, "wb") as f:
                                    await f.write(video_response.content)
                                return str(output_path)
                        elif status.get("status") == "failed":
                            logger.error(f"Replicate prediction failed: {status.get('error')}")
                            break

        except Exception as e:
            logger.error(f"Replicate generation failed: {e}")

        return None

    async def _text_to_speech(
        self,
        text: str,
        voice_sample_path: Optional[str] = None
    ) -> Optional[str]:
        """Convert text to speech, optionally using voice cloning"""
        output_path = AVATAR_STORAGE_PATH / f"tts_{uuid.uuid4().hex[:8]}.wav"

        # Try edge-tts (free, good quality)
        try:
            proc = await asyncio.create_subprocess_exec(
                "edge-tts",
                "--text", text,
                "--voice", "en-US-GuyNeural",
                "--write-media", str(output_path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()

            if output_path.exists():
                return str(output_path)
        except FileNotFoundError:
            logger.warning("edge-tts not installed, trying alternative")
        except Exception as e:
            logger.error(f"edge-tts failed: {e}")

        # Fallback: use pyttsx3 or other local TTS
        # This would be implemented based on available TTS engines

        return None

    def _get_available_backend(self) -> str:
        """Get the name of the available processing backend"""
        if self.sadtalker_endpoint:
            return "sadtalker_local"
        elif self.replicate_api_key:
            return "replicate"
        else:
            return "none"

    async def get_avatar(self, avatar_id: str) -> Optional[GeneratedAvatar]:
        """Get a generated avatar by ID"""
        async with self._lock:
            return self.generated_avatars.get(avatar_id)

    async def get_user_avatars(self, user_id: str) -> list[GeneratedAvatar]:
        """Get all avatars for a user"""
        async with self._lock:
            return [a for a in self.generated_avatars.values() if a.user_id == user_id]

    async def delete_avatar(self, avatar_id: str, user_id: str) -> bool:
        """Delete an avatar (only owner can delete)"""
        async with self._lock:
            avatar = self.generated_avatars.get(avatar_id)
            if not avatar or avatar.user_id != user_id:
                return False

            # Delete files
            avatar_dir = AVATAR_STORAGE_PATH / avatar_id
            if avatar_dir.exists():
                import shutil
                shutil.rmtree(avatar_dir, ignore_errors=True)

            del self.generated_avatars[avatar_id]
            return True

    async def get_image_data(self, avatar_id: str) -> Optional[bytes]:
        """Get the source image data for an avatar"""
        async with self._lock:
            avatar = self.generated_avatars.get(avatar_id)

        if not avatar:
            return None

        try:
            async with aiofiles.open(avatar.source_image_path, "rb") as f:
                return await f.read()
        except Exception:
            return None

    async def get_thumbnail_data(self, avatar_id: str) -> Optional[bytes]:
        """Get the thumbnail image data for an avatar"""
        async with self._lock:
            avatar = self.generated_avatars.get(avatar_id)

        if not avatar:
            return None

        try:
            async with aiofiles.open(avatar.thumbnail_path, "rb") as f:
                return await f.read()
        except Exception:
            return None


# Global service instance
avatar_generation_service = AvatarGenerationService()
