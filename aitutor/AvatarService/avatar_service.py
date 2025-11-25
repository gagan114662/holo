"""
HoloAvatar Service - Avatar Management and Streaming Backend
Supports HeyGen Streaming Avatars and Ready Player Me 3D Avatars
"""

import os
import json
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime
import base64


app = FastAPI(title="HoloAvatar Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Configuration ==============

class AvatarProvider(str, Enum):
    HEYGEN = "heygen"
    READY_PLAYER_ME = "ready_player_me"
    LOCAL_3D = "local_3d"


class AvatarType(str, Enum):
    HISTORICAL_FIGURE = "historical_figure"
    CUSTOM_TUTOR = "custom_tutor"
    STUDENT_AVATAR = "student_avatar"


# ============== Historical Figure Personas ==============

HISTORICAL_FIGURES = {
    "einstein": {
        "id": "einstein",
        "name": "Albert Einstein",
        "subject": "physics",
        "era": "20th Century",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/einstein.glb",
        "heygen_avatar_id": "josh_lite3_20230714",  # Placeholder - replace with actual
        "voice_id": "en-US-Standard-D",
        "personality": """You are Albert Einstein, the renowned physicist.
        Speak with wonder about the mysteries of the universe.
        Use thought experiments to explain complex concepts.
        Be encouraging and curious. Say things like 'Imagination is more important than knowledge.'
        Occasionally reference your work on relativity and the photoelectric effect.""",
        "greeting": "Ah, wonderful! A curious mind seeking knowledge. Tell me, what puzzles you today?",
        "subjects": ["physics", "mathematics", "philosophy of science"],
        "image": "/avatars/einstein.png"
    },
    "curie": {
        "id": "curie",
        "name": "Marie Curie",
        "subject": "chemistry",
        "era": "19th-20th Century",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/curie.glb",
        "heygen_avatar_id": "anna_lite3_20230714",  # Placeholder
        "voice_id": "en-US-Standard-F",
        "personality": """You are Marie Curie, pioneering scientist and two-time Nobel laureate.
        Speak with determination and passion for scientific discovery.
        Emphasize the importance of perseverance in research.
        Reference your work on radioactivity, polonium, and radium.
        Be inspiring, especially to young scientists.""",
        "greeting": "Bonjour! Science is about dedication and discovery. What shall we explore together?",
        "subjects": ["chemistry", "physics", "radioactivity"],
        "image": "/avatars/curie.png"
    },
    "shakespeare": {
        "id": "shakespeare",
        "name": "William Shakespeare",
        "subject": "literature",
        "era": "16th-17th Century",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/shakespeare.glb",
        "heygen_avatar_id": "josh_lite3_20230714",  # Placeholder
        "voice_id": "en-GB-Standard-B",
        "personality": """You are William Shakespeare, the Bard of Avon.
        Speak with theatrical flair and occasional Elizabethan phrases.
        Use metaphors and poetic language naturally.
        Reference your plays and sonnets when relevant.
        Help students understand literature through storytelling.""",
        "greeting": "All the world's a stage, dear student! What tale shall we unravel today?",
        "subjects": ["literature", "writing", "drama", "poetry"],
        "image": "/avatars/shakespeare.png"
    },
    "hypatia": {
        "id": "hypatia",
        "name": "Hypatia of Alexandria",
        "subject": "mathematics",
        "era": "Ancient",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/hypatia.glb",
        "heygen_avatar_id": "anna_lite3_20230714",  # Placeholder
        "voice_id": "en-US-Standard-C",
        "personality": """You are Hypatia, mathematician and philosopher of Alexandria.
        Speak with wisdom and encourage logical thinking.
        Reference ancient Greek mathematics and astronomy.
        Emphasize the beauty of mathematical proof.
        Be patient and methodical in explanations.""",
        "greeting": "Welcome, seeker of wisdom. Mathematics reveals the harmony of the cosmos. What mysteries draw your mind?",
        "subjects": ["mathematics", "astronomy", "philosophy"],
        "image": "/avatars/hypatia.png"
    },
    "darwin": {
        "id": "darwin",
        "name": "Charles Darwin",
        "subject": "biology",
        "era": "19th Century",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/darwin.glb",
        "heygen_avatar_id": "josh_lite3_20230714",  # Placeholder
        "voice_id": "en-GB-Standard-D",
        "personality": """You are Charles Darwin, naturalist and author of On the Origin of Species.
        Speak with careful observation and scientific method.
        Reference your voyage on the Beagle and studies of natural selection.
        Encourage students to observe nature carefully.
        Be thoughtful and evidence-based.""",
        "greeting": "Greetings, young naturalist! Nature has endless wonders to reveal to the patient observer. What aspect of life shall we study?",
        "subjects": ["biology", "evolution", "natural history"],
        "image": "/avatars/darwin.png"
    },
    "ada": {
        "id": "ada",
        "name": "Ada Lovelace",
        "subject": "computer_science",
        "era": "19th Century",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/ada.glb",
        "heygen_avatar_id": "anna_lite3_20230714",  # Placeholder
        "voice_id": "en-GB-Standard-A",
        "personality": """You are Ada Lovelace, the first computer programmer.
        Speak with enthusiasm about the potential of computing machines.
        Reference your work with Charles Babbage on the Analytical Engine.
        Encourage creative and analytical thinking together.
        Be visionary about technology's future.""",
        "greeting": "Delightful to meet you! The Analytical Engine weaves algebraic patterns as the Jacquard loom weaves flowers. Shall we explore the poetry of computation?",
        "subjects": ["computer_science", "mathematics", "programming"],
        "image": "/avatars/ada.png"
    },
    "socrates": {
        "id": "socrates",
        "name": "Socrates",
        "subject": "philosophy",
        "era": "Ancient",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/socrates.glb",
        "heygen_avatar_id": "josh_lite3_20230714",  # Placeholder
        "voice_id": "en-US-Standard-D",
        "personality": """You are Socrates of Athens, the philosopher.
        Use the Socratic method - ask probing questions rather than giving direct answers.
        Guide students to discover truths themselves through dialogue.
        Reference Greek philosophy and ethical reasoning.
        Be humble about your own knowledge - 'I know that I know nothing.'""",
        "greeting": "Ah, a fellow seeker of wisdom! Tell me, what do you believe you know, and how do you know it?",
        "subjects": ["philosophy", "ethics", "critical_thinking", "logic"],
        "image": "/avatars/socrates.png"
    },
    "frida": {
        "id": "frida",
        "name": "Frida Kahlo",
        "subject": "art",
        "era": "20th Century",
        "avatar_url": "https://api.readyplayer.me/v1/avatars/frida.glb",
        "heygen_avatar_id": "anna_lite3_20230714",  # Placeholder
        "voice_id": "es-US-Standard-A",  # Spanish-accented
        "personality": """You are Frida Kahlo, Mexican artist known for self-portraits.
        Speak with passion and emotional depth about art.
        Reference your unique style blending realism and surrealism.
        Encourage students to express their inner world through art.
        Be bold, honest, and inspiring about creative expression.""",
        "greeting": "Hola! Art is the only way to run away without leaving home. What colors does your soul wish to paint today?",
        "subjects": ["art", "art_history", "self_expression"],
        "image": "/avatars/frida.png"
    }
}


# ============== Pydantic Models ==============

class AvatarSession(BaseModel):
    session_id: str
    avatar_id: str
    provider: AvatarProvider
    user_id: str
    created_at: datetime
    status: str = "active"


class CreateSessionRequest(BaseModel):
    avatar_id: str
    user_id: str
    provider: AvatarProvider = AvatarProvider.HEYGEN


class SpeakRequest(BaseModel):
    session_id: str
    text: str
    emotion: Optional[str] = "neutral"


class AvatarConfig(BaseModel):
    avatar_id: str
    name: str
    provider: AvatarProvider
    voice_id: Optional[str] = None
    personality: Optional[str] = None


# ============== In-Memory Storage ==============

active_sessions: Dict[str, AvatarSession] = {}
websocket_connections: Dict[str, WebSocket] = {}


# ============== HeyGen Integration ==============

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "")
HEYGEN_API_BASE = "https://api.heygen.com"


async def create_heygen_session(avatar_id: str) -> Dict[str, Any]:
    """Create a HeyGen streaming avatar session"""
    if not HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="HEYGEN_API_KEY not configured")

    async with aiohttp.ClientSession() as session:
        # Create streaming token
        async with session.post(
            f"{HEYGEN_API_BASE}/v1/streaming.create_token",
            headers={"x-api-key": HEYGEN_API_KEY}
        ) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Failed to create HeyGen token")
            token_data = await resp.json()

        # Start streaming session
        async with session.post(
            f"{HEYGEN_API_BASE}/v1/streaming.new",
            headers={"x-api-key": HEYGEN_API_KEY},
            json={
                "avatar_id": avatar_id,
                "voice": {"voice_id": "en-US-Standard-D"},
                "quality": "high"
            }
        ) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail="Failed to create HeyGen session")
            session_data = await resp.json()

    return {
        "token": token_data.get("data", {}).get("token"),
        "session_id": session_data.get("data", {}).get("session_id"),
        "sdp": session_data.get("data", {}).get("sdp")
    }


async def heygen_speak(session_id: str, text: str) -> Dict[str, Any]:
    """Make the HeyGen avatar speak"""
    if not HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="HEYGEN_API_KEY not configured")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{HEYGEN_API_BASE}/v1/streaming.task",
            headers={"x-api-key": HEYGEN_API_KEY},
            json={
                "session_id": session_id,
                "text": text,
                "task_type": "talk"
            }
        ) as resp:
            return await resp.json()


# ============== API Endpoints ==============

@app.get("/")
async def root():
    return {"service": "HoloAvatar Service", "version": "1.0.0"}


@app.get("/avatars/historical")
async def get_historical_figures():
    """Get all available historical figure avatars"""
    return {
        "avatars": [
            {
                "id": k,
                "name": v["name"],
                "subject": v["subject"],
                "era": v["era"],
                "subjects": v["subjects"],
                "greeting": v["greeting"],
                "image": v["image"]
            }
            for k, v in HISTORICAL_FIGURES.items()
        ]
    }


@app.get("/avatars/historical/{avatar_id}")
async def get_historical_figure(avatar_id: str):
    """Get a specific historical figure avatar"""
    if avatar_id not in HISTORICAL_FIGURES:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return HISTORICAL_FIGURES[avatar_id]


@app.get("/avatars/by-subject/{subject}")
async def get_avatars_by_subject(subject: str):
    """Get avatars that teach a specific subject"""
    matching = [
        {
            "id": k,
            "name": v["name"],
            "subject": v["subject"],
            "era": v["era"],
            "greeting": v["greeting"],
            "image": v["image"]
        }
        for k, v in HISTORICAL_FIGURES.items()
        if subject.lower() in [s.lower() for s in v["subjects"]]
    ]
    return {"avatars": matching}


@app.post("/sessions/create")
async def create_session(request: CreateSessionRequest):
    """Create a new avatar session"""
    import uuid

    session_id = str(uuid.uuid4())

    if request.provider == AvatarProvider.HEYGEN:
        # Get HeyGen avatar ID from historical figure config
        figure = HISTORICAL_FIGURES.get(request.avatar_id, {})
        heygen_avatar_id = figure.get("heygen_avatar_id", request.avatar_id)

        try:
            heygen_session = await create_heygen_session(heygen_avatar_id)
            session_id = heygen_session.get("session_id", session_id)
        except Exception as e:
            # Fallback to local 3D if HeyGen fails
            print(f"HeyGen session creation failed: {e}, falling back to local 3D")
            request.provider = AvatarProvider.LOCAL_3D

    session = AvatarSession(
        session_id=session_id,
        avatar_id=request.avatar_id,
        provider=request.provider,
        user_id=request.user_id,
        created_at=datetime.now()
    )

    active_sessions[session_id] = session

    return {
        "session_id": session_id,
        "avatar_id": request.avatar_id,
        "provider": request.provider.value,
        "personality": HISTORICAL_FIGURES.get(request.avatar_id, {}).get("personality", ""),
        "greeting": HISTORICAL_FIGURES.get(request.avatar_id, {}).get("greeting", "Hello! I'm here to help you learn.")
    }


@app.post("/sessions/{session_id}/speak")
async def speak(session_id: str, request: SpeakRequest):
    """Make the avatar speak"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    if session.provider == AvatarProvider.HEYGEN:
        result = await heygen_speak(session_id, request.text)
        return result
    else:
        # For local 3D avatars, return text for TTS processing
        return {
            "text": request.text,
            "emotion": request.emotion,
            "process_locally": True
        }


@app.delete("/sessions/{session_id}")
async def end_session(session_id: str):
    """End an avatar session"""
    if session_id in active_sessions:
        del active_sessions[session_id]

    if session_id in websocket_connections:
        await websocket_connections[session_id].close()
        del websocket_connections[session_id]

    return {"status": "session ended"}


@app.get("/sessions/active")
async def get_active_sessions():
    """Get all active sessions"""
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "avatar_id": s.avatar_id,
                "provider": s.provider.value,
                "user_id": s.user_id,
                "created_at": s.created_at.isoformat()
            }
            for s in active_sessions.values()
        ]
    }


# ============== WebSocket for Real-time Avatar Control ==============

@app.websocket("/ws/avatar/{session_id}")
async def avatar_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for real-time avatar control and lip-sync data"""
    await websocket.accept()
    websocket_connections[session_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "speak":
                # Process speech request
                text = data.get("text", "")
                emotion = data.get("emotion", "neutral")

                # Send acknowledgment
                await websocket.send_json({
                    "type": "speaking_start",
                    "text": text
                })

                # For local 3D, generate visemes/lip-sync data
                if session_id in active_sessions:
                    session = active_sessions[session_id]
                    if session.provider == AvatarProvider.LOCAL_3D:
                        # Generate approximate viseme timing
                        visemes = generate_visemes(text)
                        await websocket.send_json({
                            "type": "visemes",
                            "data": visemes
                        })

                await websocket.send_json({
                    "type": "speaking_end"
                })

            elif data.get("type") == "emotion":
                # Update avatar emotion
                emotion = data.get("emotion", "neutral")
                await websocket.send_json({
                    "type": "emotion_updated",
                    "emotion": emotion
                })

            elif data.get("type") == "audio_level":
                # For lip-sync based on audio input
                level = data.get("level", 0)
                await websocket.send_json({
                    "type": "mouth_open",
                    "value": min(1.0, level * 2)  # Map audio level to mouth openness
                })

    except WebSocketDisconnect:
        if session_id in websocket_connections:
            del websocket_connections[session_id]


def generate_visemes(text: str) -> List[Dict]:
    """Generate approximate viseme data from text for lip-sync"""
    # Simplified viseme mapping - in production, use a proper TTS with viseme output
    viseme_map = {
        'a': 'aa', 'e': 'E', 'i': 'I', 'o': 'O', 'u': 'U',
        'b': 'PP', 'm': 'PP', 'p': 'PP',
        'f': 'FF', 'v': 'FF',
        'th': 'TH', 'd': 'DD', 't': 'DD', 'n': 'DD',
        's': 'SS', 'z': 'SS',
        'sh': 'CH', 'ch': 'CH', 'j': 'CH',
        'r': 'RR', 'l': 'RR',
        'k': 'kk', 'g': 'kk',
        'w': 'O', 'y': 'I'
    }

    visemes = []
    time_offset = 0
    chars_per_second = 12  # Approximate speaking speed

    text_lower = text.lower()
    i = 0
    while i < len(text_lower):
        char = text_lower[i]

        # Check for digraphs
        if i + 1 < len(text_lower):
            digraph = text_lower[i:i+2]
            if digraph in viseme_map:
                visemes.append({
                    "time": time_offset,
                    "viseme": viseme_map[digraph],
                    "duration": 0.1
                })
                time_offset += 1 / chars_per_second
                i += 2
                continue

        # Single character
        if char in viseme_map:
            visemes.append({
                "time": time_offset,
                "viseme": viseme_map[char],
                "duration": 0.08
            })
        elif char == ' ':
            visemes.append({
                "time": time_offset,
                "viseme": "sil",
                "duration": 0.05
            })

        time_offset += 1 / chars_per_second
        i += 1

    return visemes


# ============== Main ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
