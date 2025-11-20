/**
 * HoloAvatar Display Component
 * Main component for rendering the animated avatar
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import './holoavatar.scss';

interface AvatarState {
  character: string | null;
  character_name: string | null;
  is_speaking: boolean;
  expression: string;
  is_initialized: boolean;
}

interface FrameData {
  frame: string; // base64
  expression: string;
  speaking: boolean;
  timestamp: number;
}

interface HoloAvatarDisplayProps {
  websocketUrl?: string;
  onStateChange?: (state: AvatarState) => void;
  onError?: (error: string) => void;
  showControls?: boolean;
  className?: string;
}

export const HoloAvatarDisplay: React.FC<HoloAvatarDisplayProps> = ({
  websocketUrl = 'ws://localhost:8766',
  onStateChange,
  onError,
  showControls = true,
  className = ''
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [avatarState, setAvatarState] = useState<AvatarState | null>(null);
  const [characters, setCharacters] = useState<Array<{id: string, name: string, description: string}>>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(websocketUrl);

    ws.onopen = () => {
      console.log('HoloAvatar connected');
      setIsConnected(true);

      // Request initial state and character list
      ws.send(JSON.stringify({ type: 'get_state' }));
      ws.send(JSON.stringify({ type: 'get_characters' }));
    };

    ws.onclose = () => {
      console.log('HoloAvatar disconnected');
      setIsConnected(false);
      setIsStreaming(false);
    };

    ws.onerror = (error) => {
      console.error('HoloAvatar WebSocket error:', error);
      onError?.('WebSocket connection error');
    };

    ws.onmessage = (event) => {
      handleMessage(JSON.parse(event.data));
    };

    wsRef.current = ws;
  }, [websocketUrl, onError]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Handle incoming messages
  const handleMessage = useCallback((message: { type: string; payload: any }) => {
    switch (message.type) {
      case 'state':
        setAvatarState(message.payload);
        onStateChange?.(message.payload);
        break;

      case 'state_change':
        // Partial state update
        setAvatarState(prev => prev ? { ...prev, ...message.payload.data } : null);
        break;

      case 'frame':
        renderFrame(message.payload as FrameData);
        break;

      case 'audio':
        playAudio(message.payload);
        break;

      case 'characters_list':
        setCharacters(message.payload.characters);
        break;

      case 'stream_started':
        setIsStreaming(true);
        break;

      case 'stream_stopped':
        setIsStreaming(false);
        break;

      case 'error':
        console.error('Avatar error:', message.payload.message);
        onError?.(message.payload.message);
        break;
    }
  }, [onStateChange, onError]);

  // Render frame to canvas
  const renderFrame = useCallback((frameData: FrameData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw frame
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Optional: Add expression indicator
      if (frameData.speaking) {
        ctx.fillStyle = '#00ff00';
        ctx.beginPath();
        ctx.arc(canvas.width - 20, 20, 8, 0, Math.PI * 2);
        ctx.fill();
      }
    };
    img.src = `data:image/jpeg;base64,${frameData.frame}`;
  }, []);

  // Play audio
  const playAudio = useCallback(async (audioData: { data: string; format: string }) => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      // Decode base64 audio
      const binaryString = atob(audioData.data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Decode and play
      const audioBuffer = await audioContextRef.current.decodeAudioData(bytes.buffer);
      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      source.start();
    } catch (error) {
      console.error('Error playing avatar audio:', error);
    }
  }, []);

  // Send command to server
  const sendCommand = useCallback((type: string, payload: any = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  // Control functions
  const startStream = useCallback(() => {
    sendCommand('start_stream');
  }, [sendCommand]);

  const stopStream = useCallback(() => {
    sendCommand('stop_stream');
  }, [sendCommand]);

  const selectCharacter = useCallback((characterId: string) => {
    sendCommand('select_character', { character_id: characterId });
  }, [sendCommand]);

  const speak = useCallback((text: string, emotion: string = 'neutral') => {
    sendCommand('speak', { text, emotion });
  }, [sendCommand]);

  const setExpression = useCallback((expression: string, intensity: number = 0.7) => {
    sendCommand('set_expression', { expression, intensity });
  }, [sendCommand]);

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return (
    <div className={`holoavatar-display ${className}`}>
      {/* Avatar Canvas */}
      <div className="avatar-canvas-container">
        <canvas
          ref={canvasRef}
          width={512}
          height={512}
          className="avatar-canvas"
        />

        {/* Status indicators */}
        <div className="avatar-status">
          <span className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '●' : '○'}
          </span>
          {avatarState?.is_speaking && (
            <span className="speaking-indicator">Speaking...</span>
          )}
        </div>

        {/* Character name */}
        {avatarState?.character_name && (
          <div className="character-name">
            {avatarState.character_name}
          </div>
        )}
      </div>

      {/* Controls */}
      {showControls && (
        <div className="avatar-controls">
          {/* Stream controls */}
          <div className="control-group">
            {!isStreaming ? (
              <button onClick={startStream} disabled={!isConnected}>
                Start Avatar
              </button>
            ) : (
              <button onClick={stopStream}>
                Stop Avatar
              </button>
            )}
          </div>

          {/* Character selector */}
          {characters.length > 0 && (
            <div className="control-group">
              <select
                value={avatarState?.character || ''}
                onChange={(e) => selectCharacter(e.target.value)}
                disabled={!isConnected}
              >
                {characters.map(char => (
                  <option key={char.id} value={char.id}>
                    {char.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Expression buttons */}
          <div className="control-group expression-buttons">
            {['neutral', 'happy', 'thinking', 'encouraging'].map(expr => (
              <button
                key={expr}
                onClick={() => setExpression(expr)}
                disabled={!isConnected}
                className={avatarState?.expression === expr ? 'active' : ''}
              >
                {expr}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Hook for using avatar in other components
export const useHoloAvatar = (websocketUrl: string = 'ws://localhost:8766') => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(websocketUrl);
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    wsRef.current = ws;

    return () => ws.close();
  }, [websocketUrl]);

  const sendCommand = useCallback((type: string, payload: any = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  return {
    isConnected,
    speak: (text: string, emotion?: string) => sendCommand('speak', { text, emotion }),
    setExpression: (expr: string, intensity?: number) => sendCommand('set_expression', { expression: expr, intensity }),
    selectCharacter: (id: string) => sendCommand('select_character', { character_id: id }),
    triggerEvent: (event: string) => sendCommand('trigger_event', { event }),
    sendDashEvent: (eventType: string, eventData: any) => sendCommand('dash_event', { event_type: eventType, event_data: eventData }),
  };
};

export default HoloAvatarDisplay;
