/**
 * Avatar System Types
 * Defines interfaces for the HoloAvatar system
 */

export type AvatarProvider = 'heygen' | 'd-id' | 'ready_player_me' | 'local_3d' | 'local_tts';

export type AvatarEmotion =
  | 'neutral'
  | 'happy'
  | 'sad'
  | 'surprised'
  | 'thinking'
  | 'encouraging'
  | 'confused';

export interface HistoricalFigure {
  id: string;
  name: string;
  subject: string;
  era: string;
  subjects: string[];
  greeting: string;
  personality: string;
  voice_id: string;
  avatar_url: string;
  heygen_avatar_id: string;
  did_avatar_id?: string;
  image: string;
  teachingStyle?: string;
  famousQuotes?: string[];
}

export interface AvatarSession {
  session_id: string;
  avatar_id: string;
  provider: AvatarProvider;
  personality: string;
  greeting: string;
}

export interface Viseme {
  time: number;
  viseme: string;
  duration: number;
}

export interface AvatarState {
  isLoading: boolean;
  isSpeaking: boolean;
  currentEmotion: AvatarEmotion;
  currentText: string;
  error: string | null;
}

export interface AvatarProps {
  avatarId: string;
  provider?: AvatarProvider;
  onReady?: () => void;
  onSpeakingStart?: () => void;
  onSpeakingEnd?: () => void;
  onError?: (error: string) => void;
  className?: string;
}

export interface AvatarContextType {
  currentAvatar: HistoricalFigure | null;
  session: AvatarSession | null;
  state: AvatarState;
  preferredProvider: AvatarProvider;
  availableProviders: AvatarProvider[];
  selectAvatar: (avatarId: string, provider?: AvatarProvider) => Promise<void>;
  speak: (text: string, emotion?: AvatarEmotion) => Promise<void>;
  setEmotion: (emotion: AvatarEmotion) => void;
  setPreferredProvider: (provider: AvatarProvider) => void;
  endSession: () => Promise<void>;
}

// Viseme to morph target mapping for Ready Player Me avatars
export const VISEME_MORPH_MAP: Record<string, string> = {
  'sil': 'viseme_sil',
  'PP': 'viseme_PP',
  'FF': 'viseme_FF',
  'TH': 'viseme_TH',
  'DD': 'viseme_DD',
  'kk': 'viseme_kk',
  'CH': 'viseme_CH',
  'SS': 'viseme_SS',
  'nn': 'viseme_nn',
  'RR': 'viseme_RR',
  'aa': 'viseme_aa',
  'E': 'viseme_E',
  'I': 'viseme_I',
  'O': 'viseme_O',
  'U': 'viseme_U',
};

// Emotion to blend shape mapping
export const EMOTION_BLEND_MAP: Record<AvatarEmotion, Record<string, number>> = {
  neutral: {},
  happy: {
    'mouthSmile': 0.7,
    'eyeSquintLeft': 0.3,
    'eyeSquintRight': 0.3,
  },
  sad: {
    'mouthFrownLeft': 0.5,
    'mouthFrownRight': 0.5,
    'browInnerUp': 0.4,
  },
  surprised: {
    'mouthOpen': 0.5,
    'eyeWideLeft': 0.7,
    'eyeWideRight': 0.7,
    'browOuterUpLeft': 0.6,
    'browOuterUpRight': 0.6,
  },
  thinking: {
    'browInnerUp': 0.3,
    'eyeLookUpLeft': 0.4,
    'eyeLookUpRight': 0.4,
  },
  encouraging: {
    'mouthSmile': 0.5,
    'browInnerUp': 0.2,
  },
  confused: {
    'browInnerUp': 0.5,
    'mouthPucker': 0.3,
  },
};
