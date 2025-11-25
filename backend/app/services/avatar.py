"""
Avatar Service
Handles HeyGen and D-ID API integration for photorealistic avatars
"""
import httpx
import logging
from typing import Optional
from fastapi import WebSocket

from ..config import settings

logger = logging.getLogger(__name__)

# Avatar image URLs for D-ID (publicly accessible images)
AVATAR_IMAGE_URLS = {
    "einstein": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/440px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg",
    "curie": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Marie_Curie_c._1920s.jpg/440px-Marie_Curie_c._1920s.jpg",
    "newton": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg/440px-Portrait_of_Sir_Isaac_Newton%2C_1689.jpg",
    "darwin": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Charles_Darwin_seated_crop.jpg/440px-Charles_Darwin_seated_crop.jpg",
    "davinci": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Leonardo_self.jpg/440px-Leonardo_self.jpg",
    "aristotle": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Aristotle_Altemps_Inv8575.jpg/440px-Aristotle_Altemps_Inv8575.jpg",
    "hypatia": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Hypatia_portrait.png/440px-Hypatia_portrait.png",
    "turing": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Alan_Turing_Aged_16.jpg/440px-Alan_Turing_Aged_16.jpg",
}

# HTTP client timeout configuration
HTTP_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class AvatarService:
    """
    Avatar service supporting multiple providers:
    - HeyGen: High-quality video avatars
    - D-ID: Alternative video avatar provider
    - Local: Browser-based TTS fallback
    """

    def __init__(self):
        self.heygen_client = None
        self.did_client = None
        self.active_sessions: dict[str, dict] = {}
        self.websockets: dict[str, WebSocket] = {}

        if settings.heygen_api_key:
            self.heygen_client = httpx.AsyncClient(
                base_url="https://api.heygen.com/v1",
                headers={"X-Api-Key": settings.heygen_api_key},
                timeout=HTTP_TIMEOUT
            )
            logger.info("HeyGen client initialized")

        if settings.did_api_key:
            self.did_client = httpx.AsyncClient(
                base_url="https://api.d-id.com",
                headers={
                    "Authorization": f"Basic {settings.did_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=HTTP_TIMEOUT
            )
            logger.info("D-ID client initialized")
    
    async def create_heygen_session(self, avatar_id: str) -> Optional[str]:
        """Create a HeyGen streaming session"""
        if not self.heygen_client:
            return None
        
        try:
            # Map our avatar IDs to HeyGen avatar IDs
            heygen_avatar_map = {
                "einstein": "josh_lite3_20230714",  # Default HeyGen avatar
                "curie": "anna_costume1_20230421",
                # Add more mappings as you configure in HeyGen
            }
            
            heygen_id = heygen_avatar_map.get(avatar_id, "josh_lite3_20230714")
            
            response = await self.heygen_client.post(
                "/streaming.new",
                json={
                    "avatar_id": heygen_id,
                    "quality": "medium",
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("session_id")
                self.active_sessions[session_id] = {
                    "provider": "heygen",
                    "avatar_id": avatar_id,
                    "heygen_session": data
                }
                return session_id
        except httpx.TimeoutException:
            logger.error("HeyGen session creation timed out")
        except httpx.HTTPError as e:
            logger.error(f"HeyGen HTTP error: {e}")
        except Exception as e:
            logger.exception(f"HeyGen session creation failed: {e}")

        return None

    async def create_did_session(self, avatar_id: str) -> Optional[str]:
        """Create a D-ID streaming session"""
        if not self.did_client:
            logger.warning("D-ID client not configured")
            return None

        try:
            # Get the avatar image URL
            source_url = AVATAR_IMAGE_URLS.get(
                avatar_id,
                AVATAR_IMAGE_URLS.get("einstein")  # Default fallback
            )

            response = await self.did_client.post(
                "/talks/streams",
                json={
                    "source_url": source_url,
                }
            )

            if response.status_code in [200, 201]:
                data = response.json()
                session_id = data.get("id")
                self.active_sessions[session_id] = {
                    "provider": "did",
                    "avatar_id": avatar_id,
                    "did_session": data
                }
                logger.info(f"D-ID session created: {session_id}")
                return session_id
            else:
                logger.error(f"D-ID session creation failed: {response.status_code} - {response.text}")
        except httpx.TimeoutException:
            logger.error("D-ID session creation timed out")
        except httpx.HTTPError as e:
            logger.error(f"D-ID HTTP error: {e}")
        except Exception as e:
            logger.exception(f"D-ID session creation failed: {e}")
        
        return None
    
    async def speak(
        self,
        session_id: str,
        text: str,
        emotion: str = "neutral"
    ) -> dict:
        """Make the avatar speak text"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            # Local session - return data for browser TTS
            return {
                "status": "local",
                "text": text,
                "emotion": emotion,
                "visemes": self._generate_simple_visemes(text)
            }
        
        provider = session.get("provider")
        
        if provider == "heygen" and self.heygen_client:
            return await self._heygen_speak(session_id, text, emotion)
        elif provider == "did" and self.did_client:
            return await self._did_speak(session_id, text, emotion)
        
        return {
            "status": "local",
            "text": text,
            "emotion": emotion
        }
    
    async def _heygen_speak(self, session_id: str, text: str, emotion: str) -> dict:
        """Send speech to HeyGen"""
        try:
            response = await self.heygen_client.post(
                "/streaming.task",
                json={
                    "session_id": session_id,
                    "text": text,
                    "task_type": "talk"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "streaming",
                    "task_id": data.get("task_id"),
                    "provider": "heygen"
                }
        except httpx.TimeoutException:
            logger.error("HeyGen speak timed out")
        except httpx.HTTPError as e:
            logger.error(f"HeyGen speak HTTP error: {e}")
        except Exception as e:
            logger.exception(f"HeyGen speak failed: {e}")

        return {"status": "error", "message": "HeyGen speech failed"}
    
    async def _did_speak(self, session_id: str, text: str, emotion: str) -> dict:
        """Send speech to D-ID"""
        try:
            session = self.active_sessions[session_id]
            did_session = session.get("did_session", {})
            
            response = await self.did_client.post(
                f"/talks/streams/{session_id}/sdp",
                json={
                    "script": {
                        "type": "text",
                        "input": text,
                        "provider": {
                            "type": "microsoft",
                            "voice_id": "en-US-JennyNeural"
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "streaming",
                    "provider": "did"
                }
        except httpx.TimeoutException:
            logger.error("D-ID speak timed out")
        except httpx.HTTPError as e:
            logger.error(f"D-ID speak HTTP error: {e}")
        except Exception as e:
            logger.exception(f"D-ID speak failed: {e}")

        return {"status": "error", "message": "D-ID speech failed"}
    
    def _generate_simple_visemes(self, text: str) -> list:
        """Generate simple viseme timing for local TTS"""
        # Simplified viseme generation for CSS-based lip sync
        # In production, you'd get this from the TTS API
        
        visemes = []
        words = text.split()
        time = 0
        
        for word in words:
            # Rough timing: ~300ms per word
            duration = len(word) * 50  # ms per character
            
            # Simple phoneme mapping
            for char in word.lower():
                if char in 'aeiou':
                    visemes.append({
                        "time": time,
                        "viseme": "aa" if char in 'ao' else "E" if char == 'e' else "I",
                        "duration": 80
                    })
                elif char in 'bmp':
                    visemes.append({
                        "time": time,
                        "viseme": "PP",
                        "duration": 60
                    })
                elif char in 'fv':
                    visemes.append({
                        "time": time,
                        "viseme": "FF",
                        "duration": 60
                    })
                time += 60
            
            time += 100  # Pause between words
        
        return visemes
    
    async def end_session(self, session_id: str):
        """End an avatar session"""
        session = self.active_sessions.get(session_id)
        
        if session:
            provider = session.get("provider")
            
            if provider == "heygen" and self.heygen_client:
                try:
                    await self.heygen_client.post(
                        "/streaming.stop",
                        json={"session_id": session_id}
                    )
                    logger.info(f"HeyGen session ended: {session_id}")
                except Exception as e:
                    logger.warning(f"Error ending HeyGen session: {e}")
            elif provider == "did" and self.did_client:
                try:
                    await self.did_client.delete(f"/talks/streams/{session_id}")
                    logger.info(f"D-ID session ended: {session_id}")
                except Exception as e:
                    logger.warning(f"Error ending D-ID session: {e}")
            
            del self.active_sessions[session_id]
        
        # Clean up websocket
        if session_id in self.websockets:
            del self.websockets[session_id]
    
    def register_websocket(self, session_id: str, websocket: WebSocket):
        """Register a WebSocket for a session"""
        self.websockets[session_id] = websocket
    
    def unregister_websocket(self, session_id: str):
        """Unregister a WebSocket"""
        if session_id in self.websockets:
            del self.websockets[session_id]
    
    async def send_to_websocket(self, session_id: str, message: dict):
        """Send a message to a session's WebSocket"""
        ws = self.websockets.get(session_id)
        if ws:
            await ws.send_json(message)
