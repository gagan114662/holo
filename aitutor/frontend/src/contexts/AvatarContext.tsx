/**
 * Avatar Context - Global state management for the HoloAvatar system
 * Includes offline fallback for when backend API is unavailable
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
} from '../components/avatar/types';

const AVATAR_SERVICE_URL = process.env.REACT_APP_AVATAR_SERVICE_URL || 'http://localhost:8001';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8001';

// Built-in avatars for offline use (same as AvatarSelector)
const BUILT_IN_AVATARS: Record<string, HistoricalFigure> = {
  einstein: {
    id: 'einstein',
    name: 'Albert Einstein',
    subject: 'physics',
    era: '20th Century',
    subjects: ['physics', 'mathematics'],
    greeting: "Imagination is more important than knowledge. Let's explore the wonders of the universe together!",
    personality: 'Curious, playful, and encouraging. Uses thought experiments and analogies.',
    voice_id: 'en-US-GuyNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/440px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg',
  },
  curie: {
    id: 'curie',
    name: 'Marie Curie',
    subject: 'chemistry',
    era: '19th-20th Century',
    subjects: ['chemistry', 'physics'],
    greeting: "Nothing in life is to be feared, it is only to be understood. Let's discover science together!",
    personality: 'Determined, precise, and inspiring. Encourages scientific rigor.',
    voice_id: 'en-US-JennyNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Marie_Curie_c._1920s.jpg/440px-Marie_Curie_c._1920s.jpg',
  },
  shakespeare: {
    id: 'shakespeare',
    name: 'William Shakespeare',
    subject: 'literature',
    era: '16th-17th Century',
    subjects: ['literature', 'writing', 'history'],
    greeting: "All the world's a stage, and all the men and women merely players. Let us write our story together!",
    personality: 'Eloquent, dramatic, and witty. Uses metaphors and storytelling.',
    voice_id: 'en-GB-RyanNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Shakespeare.jpg/440px-Shakespeare.jpg',
  },
  hypatia: {
    id: 'hypatia',
    name: 'Hypatia of Alexandria',
    subject: 'mathematics',
    era: 'Ancient',
    subjects: ['mathematics', 'philosophy', 'astronomy'],
    greeting: 'Reserve your right to think, for even to think wrongly is better than not to think at all.',
    personality: 'Wise, patient, and philosophical. Encourages logical thinking.',
    voice_id: 'en-US-AriaNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Hypatia_portrait.png/440px-Hypatia_portrait.png',
  },
  darwin: {
    id: 'darwin',
    name: 'Charles Darwin',
    subject: 'biology',
    era: '19th Century',
    subjects: ['biology', 'science'],
    greeting: 'In the long history of humankind, those who learned to collaborate most effectively have prevailed.',
    personality: 'Observant, methodical, and gentle. Encourages natural curiosity.',
    voice_id: 'en-GB-RyanNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Charles_Darwin_seated_crop.jpg/440px-Charles_Darwin_seated_crop.jpg',
  },
  ada: {
    id: 'ada',
    name: 'Ada Lovelace',
    subject: 'computer_science',
    era: '19th Century',
    subjects: ['computer_science', 'mathematics'],
    greeting: 'The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves.',
    personality: 'Visionary, analytical, and poetic. Bridges math and imagination.',
    voice_id: 'en-GB-SoniaNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Ada_Lovelace_portrait.jpg/440px-Ada_Lovelace_portrait.jpg',
  },
  socrates: {
    id: 'socrates',
    name: 'Socrates',
    subject: 'philosophy',
    era: 'Ancient',
    subjects: ['philosophy', 'ethics'],
    greeting: 'The only true wisdom is in knowing you know nothing. Let us question everything together.',
    personality: 'Questioning, humble, and challenging. Uses Socratic method.',
    voice_id: 'en-US-GuyNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Socrate_du_Louvre.jpg/440px-Socrate_du_Louvre.jpg',
  },
  frida: {
    id: 'frida',
    name: 'Frida Kahlo',
    subject: 'art',
    era: '20th Century',
    subjects: ['art', 'history'],
    greeting: 'I paint myself because I am so often alone and because I am the subject I know best.',
    personality: 'Passionate, honest, and expressive. Encourages self-expression.',
    voice_id: 'es-MX-DaliaNeural',
    avatar_url: '',
    heygen_avatar_id: '',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg/440px-Frida_Kahlo%2C_by_Guillermo_Kahlo.jpg',
  },
};

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
  const [isOfflineMode, setIsOfflineMode] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Connect to avatar WebSocket when session is created (only in online mode)
  useEffect(() => {
    if (session?.session_id && !wsRef.current && !isOfflineMode) {
      try {
        const ws = new WebSocket(`${WS_URL}/ws/avatar/${session.session_id}`);

        ws.onopen = () => {
          console.log('Avatar WebSocket connected');
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };

        ws.onerror = () => {
          console.log('WebSocket unavailable, using offline mode');
          setIsOfflineMode(true);
        };

        ws.onclose = () => {
          wsRef.current = null;
        };

        wsRef.current = ws;
      } catch {
        setIsOfflineMode(true);
      }
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [session?.session_id, isOfflineMode]);

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
      // Try to fetch from API first
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const avatarResponse = await fetch(
        `${AVATAR_SERVICE_URL}/avatars/historical/${avatarId}`,
        { signal: controller.signal }
      );
      clearTimeout(timeoutId);

      if (!avatarResponse.ok) {
        throw new Error('Failed to fetch avatar');
      }
      const avatarData: HistoricalFigure = await avatarResponse.json();
      setCurrentAvatar(avatarData);
      setIsOfflineMode(false);

      // Create session
      const sessionResponse = await fetch(`${AVATAR_SERVICE_URL}/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          avatar_id: avatarId,
          user_id: 'current_user',
          provider: 'local_3d',
        }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to create session');
      }

      const sessionData: AvatarSession = await sessionResponse.json();
      setSession(sessionData);

      setState((prev) => ({ ...prev, isLoading: false }));

      // Speak greeting
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('avatar-speak', {
          detail: { text: avatarData.greeting, emotion: 'happy' }
        }));
      }, 500);
    } catch {
      // FALLBACK: Use built-in avatar data
      console.log('Using offline mode for avatar:', avatarId);
      setIsOfflineMode(true);

      const builtInAvatar = BUILT_IN_AVATARS[avatarId];
      if (builtInAvatar) {
        setCurrentAvatar(builtInAvatar);

        // Create local session
        const localSession: AvatarSession = {
          session_id: `local_${Date.now()}`,
          avatar_id: avatarId,
          provider: 'local_3d',
          personality: builtInAvatar.personality,
          greeting: builtInAvatar.greeting,
        };
        setSession(localSession);

        setState((prev) => ({ ...prev, isLoading: false, error: null }));

        // Speak greeting using local TTS
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('avatar-speak', {
            detail: { text: builtInAvatar.greeting, emotion: 'happy' }
          }));
        }, 500);
      } else {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: `Avatar "${avatarId}" not found`,
        }));
      }
    }
  }, []);

  const speak = useCallback(
    async (text: string, emotion: AvatarEmotion = 'neutral') => {
      // Set speaking state
      setState((prev) => ({
        ...prev,
        isSpeaking: true,
        currentText: text,
        currentEmotion: emotion,
      }));

      if (!isOfflineMode && wsRef.current?.readyState === WebSocket.OPEN) {
        // Send via WebSocket for real-time lip-sync
        wsRef.current.send(
          JSON.stringify({
            type: 'speak',
            text,
            emotion,
          })
        );
      } else if (!isOfflineMode && session) {
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
        } catch {
          // Use local TTS via event
          window.dispatchEvent(new CustomEvent('avatar-speak', {
            detail: { text, emotion }
          }));
        }
      } else {
        // Offline mode: dispatch event for VideoAvatar to handle with local TTS
        window.dispatchEvent(new CustomEvent('avatar-speak', {
          detail: { text, emotion }
        }));
      }
    },
    [session, isOfflineMode]
  );

  const setEmotion = useCallback((emotion: AvatarEmotion) => {
    setState((prev) => ({ ...prev, currentEmotion: emotion }));

    if (!isOfflineMode && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'emotion',
          emotion,
        })
      );
    }
  }, [isOfflineMode]);

  const endSession = useCallback(async () => {
    if (session && !isOfflineMode) {
      try {
        await fetch(`${AVATAR_SERVICE_URL}/sessions/${session.session_id}`, {
          method: 'DELETE',
        });
      } catch {
        // Ignore errors when ending session
      }
    }

    setSession(null);
    setCurrentAvatar(null);
    setState(initialState);

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, [session, isOfflineMode]);

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
