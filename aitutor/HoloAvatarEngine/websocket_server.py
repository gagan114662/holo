"""
WebSocket Server for HoloAvatar
Real-time communication between avatar engine and frontend
"""
import asyncio
import json
import websockets
from typing import Set, Dict, Any
import base64

from .avatar_manager import get_avatar_manager, AvatarManager
from .config import config


class AvatarWebSocketServer:
    """
    WebSocket server for avatar control and streaming

    Protocol:
    - Client -> Server: Control commands (select character, speak, set expression)
    - Server -> Client: Frame data, audio data, state updates
    """

    def __init__(self, host: str = None, port: int = None):
        self.host = host or config.websocket_host
        self.port = port or config.websocket_port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.avatar_manager: AvatarManager = None
        self._server = None

    async def start(self):
        """Start the WebSocket server"""
        print(f"Starting HoloAvatar WebSocket server on {self.host}:{self.port}")

        # Initialize avatar manager
        self.avatar_manager = get_avatar_manager()
        await self.avatar_manager.initialize()

        # Set up callbacks
        self.avatar_manager.on_frame_ready = self._broadcast_frame
        self.avatar_manager.on_audio_ready = self._broadcast_audio
        self.avatar_manager.on_state_change = self._broadcast_state

        # Start server
        self._server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=20
        )

        print(f"HoloAvatar server running on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the server"""
        if self.avatar_manager:
            await self.avatar_manager.stop_frame_generation()

        if self._server:
            self._server.close()
            await self._server.wait_closed()

        # Close all client connections
        for client in self.clients:
            await client.close()

        print("HoloAvatar server stopped")

    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle a new client connection"""
        self.clients.add(websocket)
        client_id = id(websocket)
        print(f"Client connected: {client_id}")

        try:
            # Send initial state
            await self._send_state(websocket)

            # Handle messages
            async for message in websocket:
                await self._process_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"Client disconnected: {client_id}")

    async def _process_message(
        self,
        websocket: websockets.WebSocketServerProtocol,
        message: str
    ):
        """Process incoming message from client"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type == "start_stream":
                await self.avatar_manager.start_frame_generation()
                await self._send_response(websocket, "stream_started", {})

            elif msg_type == "stop_stream":
                await self.avatar_manager.stop_frame_generation()
                await self._send_response(websocket, "stream_stopped", {})

            elif msg_type == "select_character":
                character_id = payload.get("character_id")
                await self.avatar_manager.load_character(character_id)
                await self._broadcast_state("character_changed", {
                    "character": character_id
                })

            elif msg_type == "speak":
                text = payload.get("text", "")
                emotion = payload.get("emotion", "neutral")
                language = payload.get("language")
                await self.avatar_manager.speak(text, emotion, language)

            elif msg_type == "set_expression":
                from .expression_controller import Expression
                expr_name = payload.get("expression", "neutral")
                intensity = payload.get("intensity", 0.7)
                try:
                    expr = Expression(expr_name)
                    self.avatar_manager.expression_controller.set_expression(
                        expr, intensity
                    )
                except ValueError:
                    pass

            elif msg_type == "trigger_event":
                event_name = payload.get("event")
                await self.avatar_manager.trigger_expression(event_name)

            elif msg_type == "get_state":
                await self._send_state(websocket)

            elif msg_type == "get_characters":
                characters = self.avatar_manager.get_available_characters()
                await self._send_response(websocket, "characters_list", {
                    "characters": characters
                })

            elif msg_type == "dash_event":
                event_type = payload.get("event_type")
                event_data = payload.get("event_data", {})
                await self.avatar_manager.process_dash_event(event_type, event_data)

            else:
                await self._send_error(websocket, f"Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON")
        except Exception as e:
            await self._send_error(websocket, str(e))

    async def _send_response(
        self,
        websocket: websockets.WebSocketServerProtocol,
        msg_type: str,
        payload: dict
    ):
        """Send response to specific client"""
        message = json.dumps({
            "type": msg_type,
            "payload": payload
        })
        await websocket.send(message)

    async def _send_error(
        self,
        websocket: websockets.WebSocketServerProtocol,
        error: str
    ):
        """Send error to client"""
        await self._send_response(websocket, "error", {"message": error})

    async def _send_state(self, websocket: websockets.WebSocketServerProtocol):
        """Send current state to client"""
        state = self.avatar_manager.get_state()
        await self._send_response(websocket, "state", state)

    async def _broadcast(self, msg_type: str, payload: dict):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return

        message = json.dumps({
            "type": msg_type,
            "payload": payload
        })

        await asyncio.gather(*[
            client.send(message)
            for client in self.clients
        ], return_exceptions=True)

    async def _broadcast_frame(self, frame_data: dict):
        """Broadcast frame to all clients"""
        await self._broadcast("frame", frame_data)

    async def _broadcast_audio(self, audio_bytes: bytes):
        """Broadcast audio to all clients"""
        await self._broadcast("audio", {
            "data": base64.b64encode(audio_bytes).decode('utf-8'),
            "format": "wav"
        })

    async def _broadcast_state(self, event: str, data: dict):
        """Broadcast state change to all clients"""
        await self._broadcast("state_change", {
            "event": event,
            "data": data
        })


async def run_server():
    """Run the avatar WebSocket server"""
    server = AvatarWebSocketServer()
    await server.start()

    # Keep running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()


def main():
    """Entry point for avatar server"""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
