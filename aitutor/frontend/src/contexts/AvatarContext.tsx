/**
 * Avatar Context - Global state management for the HoloAvatar system
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useEffect,
  ReactNode,
} from 'react';
import {
  AvatarContextType,
  AvatarState,
  AvatarSession,
  HistoricalFigure,
  AvatarEmotion,
  AvatarProvider,
} from '../components/avatar/types';

const AVATAR_SERVICE_URL = process.env.REACT_APP_AVATAR_SERVICE_URL || 'http://localhost:8001';

const initialState: AvatarState = {
  isLoading: false,
  isSpeaking: false,
  currentEmotion: 'neutral',
  currentText: '',
  error: null,
};

const AvatarContext = createContext<AvatarContextType | undefined>(undefined);

interface AvatarProviderProps {
  children: ReactNode;
}

export const AvatarContextProvider: React.FC<AvatarProviderProps> = ({ children }) => {
  const [currentAvatar, setCurrentAvatar] = useState<HistoricalFigure | null>(null);
  const [session, setSession] = useState<AvatarSession | null>(null);
  const [state, setState] = useState<AvatarState>(initialState);
  const wsRef = useRef<WebSocket | null>(null);

  // Connect to avatar WebSocket when session is created
  useEffect(() => {
    if (session?.session_id && !wsRef.current) {
      const ws = new WebSocket(`ws://localhost:8001/ws/avatar/${session.session_id}`);

      ws.onopen = () => {
        console.log('Avatar WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      ws.onerror = (error) => {
        console.error('Avatar WebSocket error:', error);
        setState((prev) => ({ ...prev, error: 'WebSocket connection error' }));
      };

      ws.onclose = () => {
        console.log('Avatar WebSocket closed');
        wsRef.current = null;
      };

      wsRef.current = ws;
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [session?.session_id]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'speaking_start':
        setState((prev) => ({
          ...prev,
          isSpeaking: true,
          currentText: data.text,
        }));
        break;
      case 'speaking_end':
        setState((prev) => ({
          ...prev,
          isSpeaking: false,
          currentText: '',
        }));
        break;
      case 'visemes':
        // Viseme data will be handled by the 3D avatar component
        window.dispatchEvent(
          new CustomEvent('avatar-visemes', { detail: data.data })
        );
        break;
      case 'emotion_updated':
        setState((prev) => ({
          ...prev,
          currentEmotion: data.emotion,
        }));
        break;
      case 'error':
        setState((prev) => ({
          ...prev,
          error: data.message,
        }));
        break;
    }
  };

  const selectAvatar = useCallback(async (avatarId: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Fetch avatar details
      const avatarResponse = await fetch(
        `${AVATAR_SERVICE_URL}/avatars/historical/${avatarId}`
      );
      if (!avatarResponse.ok) {
        throw new Error('Failed to fetch avatar');
      }
      const avatarData: HistoricalFigure = await avatarResponse.json();
      setCurrentAvatar(avatarData);

      // Create session
      const sessionResponse = await fetch(`${AVATAR_SERVICE_URL}/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          avatar_id: avatarId,
          user_id: 'current_user', // TODO: Get from auth
          provider: 'local_3d', // Default to local 3D for now
        }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to create session');
      }

      const sessionData: AvatarSession = await sessionResponse.json();
      setSession(sessionData);

      setState((prev) => ({ ...prev, isLoading: false }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, []);

  const speak = useCallback(
    async (text: string, emotion: AvatarEmotion = 'neutral') => {
      if (!session) {
        console.error('No active session');
        return;
      }

      // Send via WebSocket for real-time lip-sync
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'speak',
            text,
            emotion,
          })
        );
      } else {
        // Fallback to HTTP
        try {
          await fetch(`${AVATAR_SERVICE_URL}/sessions/${session.session_id}/speak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: session.session_id,
              text,
              emotion,
            }),
          });
        } catch (error) {
          console.error('Failed to speak:', error);
        }
      }
    },
    [session]
  );

  const setEmotion = useCallback((emotion: AvatarEmotion) => {
    setState((prev) => ({ ...prev, currentEmotion: emotion }));

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'emotion',
          emotion,
        })
      );
    }
  }, []);

  const endSession = useCallback(async () => {
    if (session) {
      try {
        await fetch(`${AVATAR_SERVICE_URL}/sessions/${session.session_id}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }

    setSession(null);
    setCurrentAvatar(null);
    setState(initialState);

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, [session]);

  const value: AvatarContextType = {
    currentAvatar,
    session,
    state,
    selectAvatar,
    speak,
    setEmotion,
    endSession,
  };

  return (
    <AvatarContext.Provider value={value}>{children}</AvatarContext.Provider>
  );
};

export const useAvatarContext = () => {
  const context = useContext(AvatarContext);
  if (!context) {
    throw new Error('useAvatarContext must be used within an AvatarContextProvider');
  }
  return context;
};
