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
  AvatarProvider,
} from '../components/avatar/types';
import { storageService } from '../services/StorageService';

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
  // New avatars from 2wai vision
  victoria: {
    id: 'victoria',
    name: 'Queen Victoria',
    subject: 'history',
    era: '19th Century',
    subjects: ['history', 'politics', 'empire'],
    greeting: 'I shall unveil why the Victorian age was a golden era of empire, innovation, and evolution. You may be amused and amazed.',
    personality: 'Regal, dignified, and authoritative. Speaks with imperial wisdom about the British Empire, the Industrial Revolution, and social reforms.',
    voice_id: 'en-GB-SoniaNeural',
    avatar_url: '',
    heygen_avatar_id: 'angela_lite3_20230714',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Queen_Victoria_by_Bassano.jpg/440px-Queen_Victoria_by_Bassano.jpg',
    teachingStyle: 'Formal and commanding, uses historical anecdotes from her 63-year reign',
    famousQuotes: ['We are not amused.', 'Great events make me quiet and calm; it is only trifles that irritate my nerves.'],
  },
  newton: {
    id: 'newton',
    name: 'Isaac Newton',
    subject: 'physics',
    era: '17th-18th Century',
    subjects: ['physics', 'mathematics', 'astronomy'],
    greeting: 'I shall help you understand how an apple changed the world through the magic of gravity. If I have seen further, it is by standing on the shoulders of giants.',
    personality: 'Brilliant, intense, and methodical. Explains complex physics through elegant mathematics and observation of nature.',
    voice_id: 'en-GB-RyanNeural',
    avatar_url: '',
    heygen_avatar_id: 'wayne_lite3_20230714',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg/440px-Portrait_of_Sir_Isaac_Newton%2C_1689.jpg',
    teachingStyle: 'Precise and mathematical, builds understanding from first principles',
    famousQuotes: ['If I have seen further, it is by standing on the shoulders of giants.', 'I can calculate the motion of heavenly bodies, but not the madness of people.'],
  },
  nightingale: {
    id: 'nightingale',
    name: 'Florence Nightingale',
    subject: 'science',
    era: '19th Century',
    subjects: ['science', 'mathematics', 'healthcare', 'statistics'],
    greeting: 'Just as I revolutionized healthcare, let me light the path for you. Care, courage, and innovation shall guide our learning journey together.',
    personality: 'Compassionate, pioneering, and data-driven. Uses statistics and evidence to explain concepts while emphasizing the human impact of knowledge.',
    voice_id: 'en-GB-SoniaNeural',
    avatar_url: '',
    heygen_avatar_id: 'lily_lite3_20230714',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Florence_Nightingale_%28H_Hering_NPG_x82368%29.jpg/440px-Florence_Nightingale_%28H_Hering_NPG_x82368%29.jpg',
    teachingStyle: 'Evidence-based and caring, uses data visualization and real-world examples',
    famousQuotes: ['I attribute my success to this: I never gave or took any excuse.', 'How very little can be done under the spirit of fear.'],
  },
  henry: {
    id: 'henry',
    name: 'Henry VIII',
    subject: 'history',
    era: '16th Century',
    subjects: ['history', 'politics', 'religion'],
    greeting: 'Reformation, countless battles, and yet this education suite is my finest legacy. Just do not ask me for marriage advice!',
    personality: 'Bold, charismatic, and commanding. Teaches Tudor history with dramatic flair, covering the English Reformation, politics, and the founding of the Church of England.',
    voice_id: 'en-GB-RyanNeural',
    avatar_url: '',
    heygen_avatar_id: 'josh_lite3_20230714',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Hans_Holbein%2C_the_Younger%2C_Around_1497-1543_-_Portrait_of_Henry_VIII_of_England_-_Google_Art_Project.jpg/440px-Hans_Holbein%2C_the_Younger%2C_Around_1497-1543_-_Portrait_of_Henry_VIII_of_England_-_Google_Art_Project.jpg',
    teachingStyle: 'Dramatic and engaging, uses personal stories and political intrigue',
    famousQuotes: ['If any persons shall hereafter publish books in English, they shall not contain heresy.', 'The king can do no wrong.'],
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

// Detect available providers based on API keys
const detectAvailableProviders = (): AvatarProvider[] => {
  const providers: AvatarProvider[] = ['local_tts']; // Always available
  const apiKeys = storageService.getApiKeys();

  if (apiKeys.heygen) {
    providers.unshift('heygen');
  }
  if (apiKeys.did) {
    providers.unshift('d-id');
  }

  return providers;
};

export const AvatarContextProvider: React.FC<AvatarProviderProps> = ({ children }) => {
  const [currentAvatar, setCurrentAvatar] = useState<HistoricalFigure | null>(null);
  const [session, setSession] = useState<AvatarSession | null>(null);
  const [state, setState] = useState<AvatarState>(initialState);
  const [isOfflineMode, setIsOfflineMode] = useState(false);
  const [preferredProvider, setPreferredProvider] = useState<AvatarProvider>('local_tts');
  const [availableProviders, setAvailableProviders] = useState<AvatarProvider[]>(['local_tts']);
  const wsRef = useRef<WebSocket | null>(null);

  // Check for available providers on mount
  useEffect(() => {
    const providers = detectAvailableProviders();
    setAvailableProviders(providers);
    // Default to best available provider
    if (providers.includes('heygen')) {
      setPreferredProvider('heygen');
    } else if (providers.includes('d-id')) {
      setPreferredProvider('d-id');
    }
  }, []);

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

  const selectAvatar = useCallback(async (avatarId: string, provider?: AvatarProvider) => {
    // Use specified provider or fall back to preferred provider
    const selectedProvider = provider || preferredProvider;

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

      // Create session with selected provider
      const sessionResponse = await fetch(`${AVATAR_SERVICE_URL}/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          avatar_id: avatarId,
          user_id: 'current_user',
          provider: selectedProvider,
        }),
      });

      if (!sessionResponse.ok) {
        throw new Error('Failed to create session');
      }

      const sessionData: AvatarSession = await sessionResponse.json();
      setSession(sessionData);

      setState((prev) => ({ ...prev, isLoading: false }));

      // Speak greeting - use provider-specific event
      setTimeout(() => {
        const eventName = selectedProvider === 'heygen' ? 'heygen-speak' :
                         selectedProvider === 'd-id' ? 'did-speak' : 'avatar-speak';
        window.dispatchEvent(new CustomEvent(eventName, {
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

        // Create local session with selected provider
        const localSession: AvatarSession = {
          session_id: `local_${Date.now()}`,
          avatar_id: avatarId,
          provider: selectedProvider,
          personality: builtInAvatar.personality,
          greeting: builtInAvatar.greeting,
        };
        setSession(localSession);

        setState((prev) => ({ ...prev, isLoading: false, error: null }));

        // Speak greeting using provider-specific event
        setTimeout(() => {
          const eventName = selectedProvider === 'heygen' ? 'heygen-speak' :
                           selectedProvider === 'd-id' ? 'did-speak' : 'avatar-speak';
          window.dispatchEvent(new CustomEvent(eventName, {
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
  }, [preferredProvider]);

  const speak = useCallback(
    async (text: string, emotion: AvatarEmotion = 'neutral') => {
      // Set speaking state
      setState((prev) => ({
        ...prev,
        isSpeaking: true,
        currentText: text,
        currentEmotion: emotion,
      }));

      // Determine the appropriate event based on current session provider
      const currentProvider = session?.provider || preferredProvider;

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
          // Use provider-specific event
          const eventName = currentProvider === 'heygen' ? 'heygen-speak' :
                           currentProvider === 'd-id' ? 'did-speak' : 'avatar-speak';
          window.dispatchEvent(new CustomEvent(eventName, {
            detail: { text, emotion }
          }));
        }
      } else {
        // Offline mode: dispatch event based on provider
        const eventName = currentProvider === 'heygen' ? 'heygen-speak' :
                         currentProvider === 'd-id' ? 'did-speak' : 'avatar-speak';
        window.dispatchEvent(new CustomEvent(eventName, {
          detail: { text, emotion }
        }));
      }
    },
    [session, isOfflineMode, preferredProvider]
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
    preferredProvider,
    availableProviders,
    selectAvatar,
    speak,
    setEmotion,
    setPreferredProvider,
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
