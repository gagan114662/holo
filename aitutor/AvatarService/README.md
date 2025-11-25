# HoloAvatar Service

The Avatar Service powers the HoloTutor platform's interactive avatar system, enabling students to learn from animated historical figures with real-time lip-sync and emotional expressions.

## Features

- **Historical Figure Personas**: Learn from Einstein, Curie, Shakespeare, Socrates, and more
- **Real-time Lip-sync**: Viseme-based mouth animations synchronized with speech
- **Emotion Detection**: Avatar expressions match the content being taught
- **Multi-Provider Support**: HeyGen (photorealistic) or Local 3D (canvas-based)
- **WebSocket Control**: Real-time avatar control and animation data

## API Endpoints

### GET `/avatars/historical`
Get all available historical figure avatars.

### GET `/avatars/historical/{avatar_id}`
Get details for a specific avatar.

### GET `/avatars/by-subject/{subject}`
Find avatars that teach a specific subject (physics, mathematics, literature, etc.)

### POST `/sessions/create`
Create a new avatar session.

```json
{
  "avatar_id": "einstein",
  "user_id": "student_123",
  "provider": "local_3d"
}
```

### POST `/sessions/{session_id}/speak`
Make the avatar speak with optional emotion.

```json
{
  "session_id": "abc-123",
  "text": "Let me explain the theory of relativity...",
  "emotion": "thinking"
}
```

### WebSocket `/ws/avatar/{session_id}`
Real-time avatar control with message types:
- `speak`: Trigger speech with lip-sync
- `emotion`: Update avatar emotion
- `audio_level`: Send audio level for mouth movement

## Historical Figures

| Avatar | Subject | Era |
|--------|---------|-----|
| Albert Einstein | Physics | 20th Century |
| Marie Curie | Chemistry | 19th-20th Century |
| William Shakespeare | Literature | 16th-17th Century |
| Hypatia | Mathematics | Ancient |
| Charles Darwin | Biology | 19th Century |
| Ada Lovelace | Computer Science | 19th Century |
| Socrates | Philosophy | Ancient |
| Frida Kahlo | Art | 20th Century |

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m uvicorn avatar_service:app --host 0.0.0.0 --port 8001 --reload
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HEYGEN_API_KEY` | HeyGen API key for photorealistic avatars | Optional |

## Integration with Frontend

The service integrates with the React frontend through:
1. REST API for session management and avatar selection
2. WebSocket for real-time lip-sync and emotion updates
3. Event dispatching for viseme timing data

See `frontend/src/contexts/AvatarContext.tsx` for frontend integration.
