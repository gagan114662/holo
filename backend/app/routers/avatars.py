"""
Avatars Router
Handles avatar management and HeyGen/D-ID integration
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
import json

from ..database import get_db
from ..config import settings
from ..services.avatar import AvatarService
from .auth import get_current_user, verify_websocket_token
from ..models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
avatar_service = AvatarService()


class AvatarInfo(BaseModel):
    id: str
    name: str
    subject: str
    era: str
    subjects: list[str]
    greeting: str
    personality: str
    voice_id: str
    image: str


class SpeakRequest(BaseModel):
    text: str
    emotion: str = "neutral"


class SessionInfo(BaseModel):
    session_id: str
    avatar_id: str
    provider: str
    personality: str
    greeting: str


# Built-in historical figure avatars
HISTORICAL_AVATARS = {
    "einstein": AvatarInfo(
        id="einstein",
        name="Albert Einstein",
        subject="physics",
        era="20th Century",
        subjects=["physics", "mathematics"],
        greeting="Imagination is more important than knowledge. Let's explore the wonders of the universe together!",
        personality="Curious, playful, and encouraging. Uses thought experiments and analogies.",
        voice_id="en-US-GuyNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/440px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg"
    ),
    "curie": AvatarInfo(
        id="curie",
        name="Marie Curie",
        subject="chemistry",
        era="19th-20th Century",
        subjects=["chemistry", "physics"],
        greeting="Nothing in life is to be feared, it is only to be understood. Let's discover science together!",
        personality="Determined, precise, and inspiring. Encourages scientific rigor.",
        voice_id="en-US-JennyNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Marie_Curie_c._1920s.jpg/440px-Marie_Curie_c._1920s.jpg"
    ),
    "shakespeare": AvatarInfo(
        id="shakespeare",
        name="William Shakespeare",
        subject="literature",
        era="16th-17th Century",
        subjects=["literature", "writing", "history"],
        greeting="All the world's a stage, and all the men and women merely players. Let us write our story together!",
        personality="Eloquent, dramatic, and witty. Uses metaphors and storytelling.",
        voice_id="en-GB-RyanNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Shakespeare.jpg/440px-Shakespeare.jpg"
    ),
    "hypatia": AvatarInfo(
        id="hypatia",
        name="Hypatia of Alexandria",
        subject="mathematics",
        era="Ancient",
        subjects=["mathematics", "philosophy", "astronomy"],
        greeting="Reserve your right to think, for even to think wrongly is better than not to think at all.",
        personality="Wise, patient, and philosophical. Encourages logical thinking.",
        voice_id="en-US-AriaNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Hypatia_portrait.png/440px-Hypatia_portrait.png"
    ),
    "darwin": AvatarInfo(
        id="darwin",
        name="Charles Darwin",
        subject="biology",
        era="19th Century",
        subjects=["biology", "science"],
        greeting="In the long history of humankind, those who learned to collaborate most effectively have prevailed.",
        personality="Observant, methodical, and gentle. Encourages natural curiosity.",
        voice_id="en-GB-RyanNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Charles_Darwin_seated_crop.jpg/440px-Charles_Darwin_seated_crop.jpg"
    ),
    "ada": AvatarInfo(
        id="ada",
        name="Ada Lovelace",
        subject="computer_science",
        era="19th Century",
        subjects=["computer_science", "mathematics"],
        greeting="The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves.",
        personality="Visionary, analytical, and poetic. Bridges math and imagination.",
        voice_id="en-GB-SoniaNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Ada_Lovelace_portrait.jpg/440px-Ada_Lovelace_portrait.jpg"
    ),
    "socrates": AvatarInfo(
        id="socrates",
        name="Socrates",
        subject="philosophy",
        era="Ancient",
        subjects=["philosophy", "ethics"],
        greeting="The only true wisdom is in knowing you know nothing. Let us question everything together.",
        personality="Questioning, humble, and challenging. Uses Socratic method.",
        voice_id="en-US-GuyNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Socrate_du_Louvre.jpg/440px-Socrate_du_Louvre.jpg"
    ),
    "frida": AvatarInfo(
        id="frida",
        name="Frida Kahlo",
        subject="art",
        era="20th Century",
        subjects=["art", "history"],
        greeting="I paint myself because I am so often alone and because I am the subject I know best.",
        personality="Passionate, honest, and expressive. Encourages self-expression.",
        voice_id="es-MX-DaliaNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg/440px-Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg"
    ),
    # New avatars from 2wai vision
    "victoria": AvatarInfo(
        id="victoria",
        name="Queen Victoria",
        subject="history",
        era="19th Century",
        subjects=["history", "politics", "empire"],
        greeting="I shall unveil why the Victorian age was a golden era of empire, innovation, and evolution. You may be amused and amazed.",
        personality="Regal, dignified, and authoritative. Speaks with imperial wisdom about the British Empire, the Industrial Revolution, and social reforms.",
        voice_id="en-GB-SoniaNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Queen_Victoria_by_Bassano.jpg/440px-Queen_Victoria_by_Bassano.jpg"
    ),
    "newton": AvatarInfo(
        id="newton",
        name="Isaac Newton",
        subject="physics",
        era="17th-18th Century",
        subjects=["physics", "mathematics", "astronomy"],
        greeting="I shall help you understand how an apple changed the world through the magic of gravity. If I have seen further, it is by standing on the shoulders of giants.",
        personality="Brilliant, intense, and methodical. Explains complex physics through elegant mathematics and observation of nature.",
        voice_id="en-GB-RyanNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg/440px-Portrait_of_Sir_Isaac_Newton%2C_1689.jpg"
    ),
    "nightingale": AvatarInfo(
        id="nightingale",
        name="Florence Nightingale",
        subject="science",
        era="19th Century",
        subjects=["science", "mathematics", "healthcare", "statistics"],
        greeting="Just as I revolutionized healthcare, let me light the path for you. Care, courage, and innovation shall guide our learning journey together.",
        personality="Compassionate, pioneering, and data-driven. Uses statistics and evidence to explain concepts while emphasizing the human impact of knowledge.",
        voice_id="en-GB-SoniaNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Florence_Nightingale_%28H_Hering_NPG_x82368%29.jpg/440px-Florence_Nightingale_%28H_Hering_NPG_x82368%29.jpg"
    ),
    "henry": AvatarInfo(
        id="henry",
        name="Henry VIII",
        subject="history",
        era="16th Century",
        subjects=["history", "politics", "religion"],
        greeting="Reformation, countless battles, and yet this education suite is my finest legacy. Just do not ask me for marriage advice!",
        personality="Bold, charismatic, and commanding. Teaches Tudor history with dramatic flair, covering the English Reformation, politics, and the founding of the Church of England.",
        voice_id="en-GB-RyanNeural",
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Hans_Holbein%2C_the_Younger%2C_Around_1497-1543_-_Portrait_of_Henry_VIII_of_England_-_Google_Art_Project.jpg/440px-Hans_Holbein%2C_the_Younger%2C_Around_1497-1543_-_Portrait_of_Henry_VIII_of_England_-_Google_Art_Project.jpg"
    ),
}


@router.get("/historical")
async def get_historical_avatars():
    """Get all available historical figure avatars"""
    return {"avatars": list(HISTORICAL_AVATARS.values())}


@router.get("/historical/{avatar_id}")
async def get_historical_avatar(avatar_id: str):
    """Get a specific historical avatar"""
    if avatar_id not in HISTORICAL_AVATARS:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return HISTORICAL_AVATARS[avatar_id]


@router.get("/by-subject/{subject}")
async def get_avatars_by_subject(subject: str):
    """Get avatars that teach a specific subject"""
    matching = [
        avatar for avatar in HISTORICAL_AVATARS.values()
        if subject in avatar.subjects or avatar.subject == subject
    ]
    return {"avatars": matching}


@router.post("/sessions/create")
async def create_avatar_session(
    avatar_id: str,
    user: User = Depends(get_current_user)
):
    """Create a new avatar session (for video streaming)"""
    if avatar_id not in HISTORICAL_AVATARS:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    avatar = HISTORICAL_AVATARS[avatar_id]
    
    # Create session with HeyGen or D-ID if API keys available
    session_id = None
    provider = "local_tts"
    
    if settings.heygen_api_key:
        session_id = await avatar_service.create_heygen_session(avatar_id)
        provider = "heygen"
    elif settings.did_api_key:
        session_id = await avatar_service.create_did_session(avatar_id)
        provider = "did"
    else:
        # Local session with browser TTS
        import uuid
        session_id = f"local_{uuid.uuid4().hex[:8]}"
    
    return SessionInfo(
        session_id=session_id,
        avatar_id=avatar_id,
        provider=provider,
        personality=avatar.personality,
        greeting=avatar.greeting
    )


@router.post("/sessions/{session_id}/speak")
async def speak(
    session_id: str,
    request: SpeakRequest,
    user: User = Depends(get_current_user)
):
    """Make the avatar speak text"""
    result = await avatar_service.speak(
        session_id=session_id,
        text=request.text,
        emotion=request.emotion
    )
    return result


@router.delete("/sessions/{session_id}")
async def end_avatar_session(
    session_id: str,
    user: User = Depends(get_current_user)
):
    """End an avatar session"""
    await avatar_service.end_session(session_id)
    return {"message": "Session ended"}


@router.websocket("/ws/avatar/{session_id}")
async def avatar_websocket(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket for real-time avatar lip-sync and viseme data (requires authentication)"""
    # Verify authentication
    user = await verify_websocket_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Authentication required")
        return

    # Validate session exists in avatar service
    if not avatar_service.active_sessions.get(session_id) and not session_id.startswith("local_"):
        await websocket.close(code=4003, reason="Avatar session not found")
        return

    await websocket.accept()
    logger.info(f"Avatar WebSocket connected: user={user.id}, session={session_id}")

    try:
        # Register this connection
        await avatar_service.register_websocket(session_id, websocket)

        while True:
            data = await websocket.receive_json()

            # Validate message structure
            msg_type = data.get("type")
            if not msg_type:
                await websocket.send_json({"type": "error", "message": "Missing message type"})
                continue

            if msg_type == "speak":
                text = data.get("text", "")
                if len(text) > 5000:  # Limit text length
                    await websocket.send_json({"type": "error", "message": "Text too long (max 5000 chars)"})
                    continue

                # Generate speech and send viseme data
                result = await avatar_service.speak(
                    session_id=session_id,
                    text=text,
                    emotion=data.get("emotion", "neutral")
                )
                await websocket.send_json({
                    "type": "speaking_start",
                    "text": text
                })

                # If we have viseme data, send it
                if result.get("visemes"):
                    await websocket.send_json({
                        "type": "visemes",
                        "data": result["visemes"]
                    })

            elif msg_type == "emotion":
                emotion = data.get("emotion", "neutral")
                valid_emotions = ["neutral", "happy", "sad", "surprised", "angry", "thinking"]
                if emotion not in valid_emotions:
                    emotion = "neutral"
                await websocket.send_json({
                    "type": "emotion_updated",
                    "emotion": emotion
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"Avatar WebSocket disconnected: session={session_id}")
        await avatar_service.unregister_websocket(session_id)
    except Exception as e:
        logger.error(f"Avatar WebSocket error: {e}")
        await avatar_service.unregister_websocket(session_id)
