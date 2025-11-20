# HoloAvatar Engine

**Cutting-edge open-source avatar system for AI Tutor**

Zero API costs, matching or exceeding paid solutions like ElevenLabs and Heygen.

## Features

- **XTTS-v2 TTS**: Voice cloning from 6-second sample, 17+ languages, <150ms latency
- **LivePortrait Animation**: Real-time portrait animation at 12.8ms/frame (RTX 4090)
- **Context-Aware Expressions**: Avatar reacts to student performance
- **DASH Integration**: Connected to adaptive learning system

## Architecture

```
HoloAvatarEngine/
├── avatar_manager.py      # Main orchestration
├── tts_engine.py          # XTTS-v2 text-to-speech
├── talking_head.py        # LivePortrait animation
├── expression_controller.py # Emotion/expression system
├── websocket_server.py    # Real-time communication
├── config.py              # Configuration
├── run_avatar.py          # Entry point
└── avatars/               # Character assets
    ├── models/            # Portrait images
    ├── voices/            # Voice samples
    └── expressions/       # Expression data
```

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# For GPU acceleration (recommended)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install XTTS-v2
pip install TTS

# Optional: Install LivePortrait for full animation
pip install liveportrait
# Or for TensorRT acceleration (fastest):
pip install faster-liveportrait
```

## Usage

### Start Server

```bash
# From aitutor directory
python -m HoloAvatarEngine.run_avatar

# Or use the main run script
./run_tutor.sh
```

### WebSocket API

Connect to `ws://localhost:8766`

**Commands:**

```javascript
// Start avatar streaming
{ "type": "start_stream" }

// Select character
{ "type": "select_character", "payload": { "character_id": "einstein" } }

// Make avatar speak
{ "type": "speak", "payload": { "text": "Hello!", "emotion": "happy" } }

// Set expression
{ "type": "set_expression", "payload": { "expression": "thinking", "intensity": 0.8 } }

// Send DASH learning event
{ "type": "dash_event", "payload": {
    "event_type": "question_answered",
    "event_data": { "is_correct": true, "response_time": 5 }
  }
}
```

**Server Messages:**

```javascript
// Frame data (30 FPS)
{ "type": "frame", "payload": { "frame": "base64...", "expression": "happy", "speaking": true } }

// Audio data
{ "type": "audio", "payload": { "data": "base64...", "format": "wav" } }

// State updates
{ "type": "state", "payload": { "character": "teacher", "is_speaking": false, ... } }
```

## Frontend Integration

```tsx
import { HoloAvatarDisplay, useHoloAvatar } from './components/holoavatar';

// Display component
<HoloAvatarDisplay
  websocketUrl="ws://localhost:8766"
  showControls={true}
  onStateChange={(state) => console.log(state)}
/>

// Hook for custom integration
const { speak, setExpression, sendDashEvent } = useHoloAvatar();

// Make avatar speak
speak("Great job solving that equation!", "happy");

// React to student answer
sendDashEvent("question_answered", { is_correct: true, response_time: 3 });
```

## Characters

| ID | Name | Best For |
|----|------|----------|
| `teacher` | Friendly Teacher | All subjects |
| `einstein` | Albert Einstein | Physics, Math |
| `curie` | Marie Curie | Chemistry, Science |
| `lovelace` | Ada Lovelace | CS, Math |

### Adding Custom Characters

1. Add portrait image to `avatars/models/{character_id}/portrait.png`
2. Add voice sample to `avatars/voices/{character_id}_sample.wav` (6+ seconds)
3. Register in `talking_head.py` AVATAR_PRESETS and `tts_engine.py` VOICE_PRESETS

## Performance

| Component | Latency | Hardware |
|-----------|---------|----------|
| TTS (XTTS-v2) | <150ms | GPU |
| Animation (LivePortrait) | 12.8ms | RTX 4090 |
| Animation (TensorRT) | 30+ FPS | RTX 3090 |
| WebSocket | <50ms | Network |

## Expression System

The avatar automatically reacts to learning events:

- **Correct Answer (Fast)** → Excited
- **Correct Answer** → Happy
- **Incorrect Answer** → Thoughtful
- **Student Struggling** → Concerned
- **Skill Mastered** → Proud

## Configuration

Set environment variables:

```bash
export AVATAR_DEVICE=cuda       # or cpu
export AVATAR_USE_TENSORRT=true # for faster inference
export AVATAR_FPS=30            # target framerate
export AVATAR_ENABLED=true      # enable in run_tutor.sh
```

## Development

```bash
# Run in development mode
python -m HoloAvatarEngine.run_avatar

# Test TTS
python -c "from HoloAvatarEngine.tts_engine import TTSEngine; import asyncio; asyncio.run(TTSEngine().synthesize('Hello world'))"

# Test avatar manager
python -c "from HoloAvatarEngine.avatar_manager import get_avatar_manager; import asyncio; asyncio.run(get_avatar_manager().initialize())"
```

## License

Open source - matching 2wai's vision of accessible education technology.
