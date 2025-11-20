"""
HoloAvatar Engine Configuration
"""
import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TTSConfig:
    """Text-to-Speech configuration using XTTS-v2"""
    model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    device: str = "cuda"  # or "cpu"
    compute_type: str = "float16"  # float16 for speed, float32 for quality
    sample_rate: int = 24000
    language: str = "en"
    # Voice cloning settings
    speaker_wav: Optional[str] = None  # Path to reference voice sample

@dataclass
class TalkingHeadConfig:
    """LivePortrait / MuseTalk configuration"""
    engine: str = "liveportrait"  # "liveportrait" or "musetalk"
    device: str = "cuda"
    use_tensorrt: bool = True  # Enable TensorRT for 12.8ms inference
    output_fps: int = 30
    output_resolution: tuple = (512, 512)
    # LivePortrait specific
    retargeting_factor: float = 1.0
    stitching_enabled: bool = True

@dataclass
class ExpressionConfig:
    """Facial expression and emotion configuration"""
    enabled: bool = True
    auto_react: bool = True  # React to student performance
    blend_duration_ms: int = 300
    idle_animations: bool = True
    # Expression intensity defaults
    default_intensity: float = 0.7

@dataclass
class AvatarConfig:
    """Main avatar configuration"""
    # Server settings
    websocket_host: str = "localhost"
    websocket_port: int = 8766

    # Performance
    target_fps: int = 30
    max_queue_size: int = 10

    # Components
    tts: TTSConfig = field(default_factory=TTSConfig)
    talking_head: TalkingHeadConfig = field(default_factory=TalkingHeadConfig)
    expressions: ExpressionConfig = field(default_factory=ExpressionConfig)

    # Paths
    avatars_dir: str = "avatars"
    models_dir: str = "avatars/models"
    voices_dir: str = "avatars/voices"

    # Default character
    default_character: str = "teacher"

# Global config instance
config = AvatarConfig()

def load_config(config_path: str = None) -> AvatarConfig:
    """Load configuration from file or environment"""
    global config

    # Override with environment variables
    if os.getenv("AVATAR_DEVICE"):
        config.tts.device = os.getenv("AVATAR_DEVICE")
        config.talking_head.device = os.getenv("AVATAR_DEVICE")

    if os.getenv("AVATAR_USE_TENSORRT"):
        config.talking_head.use_tensorrt = os.getenv("AVATAR_USE_TENSORRT").lower() == "true"

    if os.getenv("AVATAR_FPS"):
        config.target_fps = int(os.getenv("AVATAR_FPS"))
        config.talking_head.output_fps = int(os.getenv("AVATAR_FPS"))

    return config
