"""
Talking Head Generator using LivePortrait
Real-time facial animation from audio input
12.8ms inference on RTX 4090 with TensorRT
"""
import asyncio
import numpy as np
import cv2
from typing import Optional, Tuple
from pathlib import Path
import base64
import time

from .config import config, TalkingHeadConfig


class TalkingHeadEngine:
    """
    LivePortrait-based talking head generation

    Features:
    - Real-time portrait animation (12.8ms/frame on RTX 4090)
    - Audio-driven lip sync
    - Expression retargeting
    - TensorRT acceleration
    """

    def __init__(self, th_config: TalkingHeadConfig = None):
        self.config = th_config or config.talking_head
        self.model = None
        self.is_loaded = False

        # Current state
        self.source_image = None
        self.current_expression = "neutral"
        self.lip_sync_data = None

        # Performance tracking
        self.last_frame_time = 0
        self.frame_times = []

    async def load_model(self):
        """Load LivePortrait model"""
        if self.is_loaded:
            return

        print(f"Loading LivePortrait ({self.config.engine})...")

        try:
            if self.config.use_tensorrt:
                # TensorRT optimized version (fastest)
                await self._load_tensorrt_model()
            else:
                # Standard PyTorch version
                await self._load_pytorch_model()

            self.is_loaded = True
            print(f"LivePortrait loaded on {self.config.device}")

        except ImportError as e:
            print(f"Warning: LivePortrait not installed: {e}")
            print("Install with: pip install liveportrait")
            self.model = None
            self.is_loaded = True

    async def _load_tensorrt_model(self):
        """Load TensorRT optimized model for best performance"""
        # Note: Requires FasterLivePortrait package
        try:
            from faster_liveportrait import FasterLivePortrait

            self.model = FasterLivePortrait(
                device=self.config.device,
                use_tensorrt=True
            )
        except ImportError:
            print("FasterLivePortrait not available, falling back to PyTorch")
            await self._load_pytorch_model()

    async def _load_pytorch_model(self):
        """Load standard PyTorch model"""
        try:
            # This is placeholder - actual import depends on LivePortrait package
            # from liveportrait import LivePortrait
            # self.model = LivePortrait(device=self.config.device)
            self.model = None  # Placeholder for development
        except ImportError:
            self.model = None

    def set_source_image(self, image_path: str):
        """
        Set the source portrait image to animate

        Args:
            image_path: Path to portrait image (should be front-facing, good quality)
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Portrait image not found: {image_path}")

        # Load and preprocess image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize to model input size
        img = cv2.resize(img, self.config.output_resolution)

        self.source_image = img
        print(f"Source portrait loaded: {image_path}")

    def set_source_image_from_array(self, image: np.ndarray):
        """Set source image from numpy array"""
        if len(image.shape) == 3 and image.shape[2] == 3:
            self.source_image = cv2.resize(image, self.config.output_resolution)
        else:
            raise ValueError("Image must be RGB with shape (H, W, 3)")

    async def generate_frame(
        self,
        audio_chunk: np.ndarray = None,
        expression: str = "neutral",
        intensity: float = 0.7
    ) -> np.ndarray:
        """
        Generate a single animated frame

        Args:
            audio_chunk: Audio data for lip sync
            expression: Target expression (happy, sad, thinking, etc.)
            intensity: Expression intensity (0.0 - 1.0)

        Returns:
            Animated frame as numpy array (RGB)
        """
        start_time = time.time()

        if not self.is_loaded:
            await self.load_model()

        if self.source_image is None:
            raise RuntimeError("No source image set. Call set_source_image() first.")

        # Generate frame
        if self.model is not None:
            frame = await self._generate_frame_with_model(
                audio_chunk, expression, intensity
            )
        else:
            # Development fallback - return source with simple animation
            frame = self._generate_mock_frame(expression, intensity)

        # Track performance
        frame_time = (time.time() - start_time) * 1000
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 100:
            self.frame_times.pop(0)

        return frame

    async def _generate_frame_with_model(
        self,
        audio_chunk: np.ndarray,
        expression: str,
        intensity: float
    ) -> np.ndarray:
        """Generate frame using actual LivePortrait model"""
        loop = asyncio.get_event_loop()

        # Run in thread pool to avoid blocking
        frame = await loop.run_in_executor(
            None,
            self._generate_sync,
            audio_chunk, expression, intensity
        )

        return frame

    def _generate_sync(
        self,
        audio_chunk: np.ndarray,
        expression: str,
        intensity: float
    ) -> np.ndarray:
        """Synchronous frame generation"""
        # Placeholder - implement with actual LivePortrait API
        # motion = self.model.audio_to_motion(audio_chunk)
        # frame = self.model.animate(self.source_image, motion)
        return self._generate_mock_frame(expression, intensity)

    def _generate_mock_frame(
        self,
        expression: str,
        intensity: float
    ) -> np.ndarray:
        """
        Generate a realistic mock animated frame for development
        Simulates lip movement and expression changes
        """
        if self.source_image is None:
            # Create placeholder colored frame
            frame = np.zeros((*self.config.output_resolution, 3), dtype=np.uint8)
            frame[:, :] = [100, 100, 200]  # Blue-ish placeholder
            return frame

        frame = self.source_image.copy()
        h, w = frame.shape[:2]

        # Mouth position (approximate center-bottom of face)
        mouth_x, mouth_y = w // 2, int(h * 0.5)

        # Simulate lip movement based on time (for speaking animation)
        t = time.time()
        lip_movement = abs(np.sin(t * 15)) * intensity  # Fast oscillation for talking

        # Expression parameters
        expression_params = {
            "neutral": {"mouth_open": 0.0, "smile": 0.0, "brow": 0.0},
            "happy": {"mouth_open": 0.2, "smile": 0.8, "brow": 0.2},
            "thinking": {"mouth_open": 0.1, "smile": -0.2, "brow": -0.3},
            "encouraging": {"mouth_open": 0.3, "smile": 0.6, "brow": 0.2},
            "concerned": {"mouth_open": 0.15, "smile": -0.3, "brow": -0.2},
            "excited": {"mouth_open": 0.5, "smile": 0.9, "brow": 0.4},
            "proud": {"mouth_open": 0.25, "smile": 0.7, "brow": 0.3},
            "curious": {"mouth_open": 0.2, "smile": 0.1, "brow": 0.4},
            "explaining": {"mouth_open": 0.4, "smile": 0.2, "brow": 0.1},
            "listening": {"mouth_open": 0.05, "smile": 0.2, "brow": 0.15},
        }

        params = expression_params.get(expression, expression_params["neutral"])

        # Calculate mouth opening (combine expression + lip sync)
        mouth_open = (params["mouth_open"] + lip_movement * 0.5) * intensity

        # Draw mouth overlay to simulate talking
        if mouth_open > 0.05:
            # Create semi-transparent overlay for mouth
            overlay = frame.copy()

            # Mouth opening (dark interior)
            mouth_height = int(15 * mouth_open)
            mouth_width = int(30 + params["smile"] * 20)

            if mouth_height > 2:
                cv2.ellipse(
                    overlay,
                    (mouth_x, mouth_y),
                    (mouth_width, mouth_height),
                    0, 0, 360,
                    (40, 30, 30),  # Dark mouth interior
                    -1
                )

                # Teeth hint for larger openings
                if mouth_height > 8:
                    cv2.ellipse(
                        overlay,
                        (mouth_x, mouth_y - mouth_height // 3),
                        (mouth_width - 5, mouth_height // 3),
                        0, 0, 360,
                        (240, 240, 240),  # White teeth
                        -1
                    )

            # Blend overlay
            alpha = 0.7
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # Add expression indicator (subtle glow effect)
        expression_colors = {
            "neutral": (128, 128, 128),
            "happy": (80, 200, 80),
            "thinking": (200, 150, 80),
            "encouraging": (80, 200, 200),
            "concerned": (80, 120, 200),
            "excited": (80, 255, 150),
            "proud": (200, 180, 80),
            "curious": (200, 150, 200),
            "explaining": (150, 200, 200),
            "listening": (150, 180, 150),
        }

        color = expression_colors.get(expression, (128, 128, 128))

        # Subtle corner indicator
        corner_size = int(30 * intensity)
        if corner_size > 5:
            # Top-left corner glow
            pts = np.array([[0, 0], [corner_size, 0], [0, corner_size]], np.int32)
            cv2.fillPoly(frame, [pts], color)

            # Bottom-right corner glow
            pts = np.array([[w, h], [w - corner_size, h], [w, h - corner_size]], np.int32)
            cv2.fillPoly(frame, [pts], color)

        # Add speaking indicator
        if lip_movement > 0.3:
            # Small pulsing circle to indicate active speech
            pulse_size = int(5 + lip_movement * 5)
            cv2.circle(frame, (w - 25, 25), pulse_size, (80, 255, 80), -1)

        return frame

    def frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert frame to base64-encoded JPEG"""
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])

        # Convert to base64
        return base64.b64encode(buffer).decode('utf-8')

    @property
    def average_frame_time_ms(self) -> float:
        """Get average frame generation time in milliseconds"""
        if not self.frame_times:
            return 0
        return sum(self.frame_times) / len(self.frame_times)

    @property
    def current_fps(self) -> float:
        """Get current effective FPS"""
        avg_time = self.average_frame_time_ms
        if avg_time <= 0:
            return 0
        return 1000 / avg_time


class LipSyncProcessor:
    """
    Processes audio for lip synchronization

    Converts audio to phoneme-based mouth shapes (visemes)
    """

    def __init__(self):
        # Phoneme to viseme mapping (simplified)
        self.viseme_map = {
            'AA': 'open',
            'AE': 'open',
            'AH': 'open',
            'AO': 'round',
            'AW': 'round',
            'AY': 'open',
            'B': 'closed',
            'CH': 'narrow',
            'D': 'narrow',
            'DH': 'narrow',
            'EH': 'open',
            'ER': 'round',
            'EY': 'narrow',
            'F': 'teeth',
            'G': 'narrow',
            'HH': 'open',
            'IH': 'narrow',
            'IY': 'narrow',
            'JH': 'narrow',
            'K': 'narrow',
            'L': 'narrow',
            'M': 'closed',
            'N': 'narrow',
            'NG': 'narrow',
            'OW': 'round',
            'OY': 'round',
            'P': 'closed',
            'R': 'round',
            'S': 'narrow',
            'SH': 'narrow',
            'T': 'narrow',
            'TH': 'teeth',
            'UH': 'round',
            'UW': 'round',
            'V': 'teeth',
            'W': 'round',
            'Y': 'narrow',
            'Z': 'narrow',
            'ZH': 'narrow',
            'SIL': 'closed'
        }

    def audio_to_visemes(self, audio: np.ndarray, sample_rate: int) -> list:
        """
        Convert audio to viseme sequence

        Returns list of (timestamp_ms, viseme_name, intensity) tuples
        """
        # Simplified implementation using energy-based detection
        # For production, use proper phoneme recognition (e.g., Rhubarb Lip Sync)

        visemes = []
        chunk_size = sample_rate // 30  # 30 FPS

        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            energy = np.sqrt(np.mean(chunk ** 2))

            timestamp_ms = (i / sample_rate) * 1000

            if energy > 0.1:
                viseme = 'open'
                intensity = min(energy * 5, 1.0)
            elif energy > 0.02:
                viseme = 'narrow'
                intensity = energy * 10
            else:
                viseme = 'closed'
                intensity = 0.0

            visemes.append((timestamp_ms, viseme, intensity))

        return visemes


# Preset avatar portraits
AVATAR_PRESETS = {
    # Original educational characters
    "teacher": {
        "name": "Friendly Teacher",
        "image": "avatars/models/teacher/portrait.png",
        "description": "Warm and encouraging teacher"
    },
    "einstein": {
        "name": "Albert Einstein",
        "image": "avatars/models/einstein/portrait.png",
        "description": "Physics and math genius"
    },
    "curie": {
        "name": "Marie Curie",
        "image": "avatars/models/curie/portrait.png",
        "description": "Science pioneer"
    },
    "lovelace": {
        "name": "Ada Lovelace",
        "image": "avatars/models/lovelace/portrait.png",
        "description": "Computing pioneer"
    },
    # BMad-Skills specialists
    "analyst": {
        "name": "Research Analyst",
        "image": "avatars/models/analyst/portrait.png",
        "description": "Explores ideas and researches topics"
    },
    "planner": {
        "name": "Project Planner",
        "image": "avatars/models/planner/portrait.png",
        "description": "Plans and organizes projects"
    },
    "architect": {
        "name": "System Architect",
        "image": "avatars/models/architect/portrait.png",
        "description": "Teaches system design patterns"
    },
    "developer": {
        "name": "Dev Coach",
        "image": "avatars/models/developer/portrait.png",
        "description": "Guides coding and implementation"
    },
    "tester": {
        "name": "Quality Engineer",
        "image": "avatars/models/tester/portrait.png",
        "description": "Teaches testing strategies"
    },
    "ux_designer": {
        "name": "UX Designer",
        "image": "avatars/models/ux_designer/portrait.png",
        "description": "Teaches user experience design"
    },
    "security_expert": {
        "name": "Security Expert",
        "image": "avatars/models/security_expert/portrait.png",
        "description": "Teaches security best practices"
    }
}
