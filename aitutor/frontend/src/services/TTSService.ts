/**
 * Text-to-Speech Service with Real-time Lip-Sync
 * Uses Web Speech API with audio analysis for mouth movement
 */

export interface TTSOptions {
  voice?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
  language?: string;
}

export interface LipSyncData {
  mouthOpen: number; // 0-1
  viseme: string;
  timestamp: number;
}

type LipSyncCallback = (data: LipSyncData) => void;
type SpeechEventCallback = () => void;

class TTSService {
  private synth: SpeechSynthesis;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private voices: SpeechSynthesisVoice[] = [];
  private isSpeaking: boolean = false;
  private lipSyncInterval: number | null = null;
  private onLipSync: LipSyncCallback | null = null;
  private onStart: SpeechEventCallback | null = null;
  private onEnd: SpeechEventCallback | null = null;

  // Voice mapping for historical figures
  private voiceMapping: Record<string, { lang: string; gender: 'male' | 'female'; accent?: string }> = {
    einstein: { lang: 'en-US', gender: 'male', accent: 'german' },
    curie: { lang: 'en-US', gender: 'female', accent: 'french' },
    shakespeare: { lang: 'en-GB', gender: 'male' },
    hypatia: { lang: 'en-US', gender: 'female' },
    darwin: { lang: 'en-GB', gender: 'male' },
    ada: { lang: 'en-GB', gender: 'female' },
    socrates: { lang: 'en-US', gender: 'male' },
    frida: { lang: 'es-MX', gender: 'female' },
  };

  constructor() {
    this.synth = window.speechSynthesis;
    this.loadVoices();

    // Voices load asynchronously
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = () => this.loadVoices();
    }
  }

  private loadVoices(): void {
    this.voices = this.synth.getVoices();
  }

  getAvailableVoices(): SpeechSynthesisVoice[] {
    return this.voices;
  }

  getBestVoiceForAvatar(avatarId: string): SpeechSynthesisVoice | null {
    const mapping = this.voiceMapping[avatarId];
    if (!mapping) return this.voices[0] || null;

    // Try to find matching voice
    const candidates = this.voices.filter(v => {
      const langMatch = v.lang.startsWith(mapping.lang.split('-')[0]);
      const genderMatch = mapping.gender === 'female'
        ? v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('woman') || v.name.includes('Zira') || v.name.includes('Jenny')
        : !v.name.toLowerCase().includes('female') && !v.name.toLowerCase().includes('woman');
      return langMatch && genderMatch;
    });

    // Prioritize by quality
    const premium = candidates.find(v =>
      v.name.includes('Neural') || v.name.includes('Premium') || v.name.includes('Natural')
    );

    return premium || candidates[0] || this.voices.find(v => v.lang.startsWith(mapping.lang.split('-')[0])) || this.voices[0] || null;
  }

  setLipSyncCallback(callback: LipSyncCallback | null): void {
    this.onLipSync = callback;
  }

  setEventCallbacks(onStart: SpeechEventCallback | null, onEnd: SpeechEventCallback | null): void {
    this.onStart = onStart;
    this.onEnd = onEnd;
  }

  /**
   * Speak text with real-time lip-sync
   */
  async speak(text: string, options: TTSOptions = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isSpeaking) {
        this.stop();
      }

      const utterance = new SpeechSynthesisUtterance(text);

      // Set voice
      if (options.voice) {
        const voice = this.voices.find(v => v.name === options.voice || v.voiceURI === options.voice);
        if (voice) utterance.voice = voice;
      }

      // Set other options
      utterance.rate = options.rate || 0.9;
      utterance.pitch = options.pitch || 1.0;
      utterance.volume = options.volume || 1.0;
      if (options.language) utterance.lang = options.language;

      // Track speaking state
      utterance.onstart = () => {
        this.isSpeaking = true;
        this.startLipSyncAnalysis(text);
        this.onStart?.();
      };

      utterance.onend = () => {
        this.isSpeaking = false;
        this.stopLipSyncAnalysis();
        this.onEnd?.();
        resolve();
      };

      utterance.onerror = (event) => {
        this.isSpeaking = false;
        this.stopLipSyncAnalysis();
        this.onEnd?.();
        reject(new Error(event.error));
      };

      // Handle boundary events for more accurate lip-sync
      utterance.onboundary = (event) => {
        if (event.name === 'word' && this.onLipSync) {
          // Simulate stronger mouth movement on word boundaries
          this.onLipSync({
            mouthOpen: 0.6 + Math.random() * 0.3,
            viseme: this.getVisemeForChar(text.charAt(event.charIndex) || 'a'),
            timestamp: Date.now(),
          });
        }
      };

      this.synth.speak(utterance);
    });
  }

  /**
   * Speak with avatar-specific voice
   */
  async speakAsAvatar(text: string, avatarId: string): Promise<void> {
    const voice = this.getBestVoiceForAvatar(avatarId);
    return this.speak(text, {
      voice: voice?.name,
      rate: 0.9,
      pitch: this.voiceMapping[avatarId]?.gender === 'female' ? 1.1 : 0.95,
    });
  }

  private startLipSyncAnalysis(text: string): void {
    if (!this.onLipSync) return;

    // Estimate speech duration (rough: 150ms per character at normal rate)
    const estimatedDuration = text.length * 100;
    let charIndex = 0;
    const startTime = Date.now();

    this.lipSyncInterval = window.setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = elapsed / estimatedDuration;

      if (progress >= 1 || charIndex >= text.length) {
        this.stopLipSyncAnalysis();
        return;
      }

      // Get current character and generate lip-sync
      const char = text.charAt(Math.floor(progress * text.length)).toLowerCase();
      const viseme = this.getVisemeForChar(char);
      const mouthOpen = this.getMouthOpenForViseme(viseme);

      // Add some natural variation
      const variation = (Math.sin(elapsed / 100) * 0.15) + (Math.random() * 0.1);

      this.onLipSync?.({
        mouthOpen: Math.max(0, Math.min(1, mouthOpen + variation)),
        viseme,
        timestamp: Date.now(),
      });

      charIndex++;
    }, 50); // 20 FPS lip-sync
  }

  private stopLipSyncAnalysis(): void {
    if (this.lipSyncInterval) {
      clearInterval(this.lipSyncInterval);
      this.lipSyncInterval = null;
    }

    // Close mouth
    this.onLipSync?.({
      mouthOpen: 0,
      viseme: 'sil',
      timestamp: Date.now(),
    });
  }

  private getVisemeForChar(char: string): string {
    const visemeMap: Record<string, string> = {
      'a': 'aa', 'e': 'E', 'i': 'I', 'o': 'O', 'u': 'U',
      'b': 'PP', 'm': 'PP', 'p': 'PP',
      'f': 'FF', 'v': 'FF',
      'd': 'DD', 't': 'DD', 'n': 'nn', 'l': 'nn',
      's': 'SS', 'z': 'SS', 'c': 'SS',
      'r': 'RR',
      'k': 'kk', 'g': 'kk',
      'w': 'O', 'y': 'I',
      'h': 'E',
      'j': 'CH', 'x': 'SS', 'q': 'kk',
      ' ': 'sil', '.': 'sil', ',': 'sil', '!': 'sil', '?': 'sil',
    };
    return visemeMap[char] || 'DD';
  }

  private getMouthOpenForViseme(viseme: string): number {
    const mouthOpenMap: Record<string, number> = {
      'sil': 0.0,
      'PP': 0.15,
      'FF': 0.25,
      'TH': 0.3,
      'DD': 0.4,
      'kk': 0.35,
      'CH': 0.4,
      'SS': 0.2,
      'nn': 0.35,
      'RR': 0.45,
      'aa': 0.8,
      'E': 0.5,
      'I': 0.35,
      'O': 0.6,
      'U': 0.45,
    };
    return mouthOpenMap[viseme] || 0.4;
  }

  stop(): void {
    this.synth.cancel();
    this.isSpeaking = false;
    this.stopLipSyncAnalysis();
  }

  pause(): void {
    this.synth.pause();
  }

  resume(): void {
    this.synth.resume();
  }

  getIsSpeaking(): boolean {
    return this.isSpeaking || this.synth.speaking;
  }
}

export const ttsService = new TTSService();
export default TTSService;
