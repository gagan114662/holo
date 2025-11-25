/**
 * useAvatarSpeech Hook
 * Connects Gemini Live API audio output to avatar lip-sync
 * Analyzes audio levels and text for avatar animation
 */

import { useEffect, useRef, useCallback } from 'react';
import { useLiveAPIContext } from '../contexts/LiveAPIContext';
import { useAvatarContext } from '../contexts/AvatarContext';
import { AvatarEmotion } from '../components/avatar/types';

interface UseAvatarSpeechOptions {
  enabled?: boolean;
  emotionDetection?: boolean;
}

// Simple emotion detection from text
function detectEmotion(text: string): AvatarEmotion {
  const lowerText = text.toLowerCase();

  // Positive emotions
  if (
    lowerText.includes('great') ||
    lowerText.includes('excellent') ||
    lowerText.includes('wonderful') ||
    lowerText.includes('fantastic') ||
    lowerText.includes('correct') ||
    lowerText.includes('well done') ||
    lowerText.includes('exactly')
  ) {
    return 'happy';
  }

  // Encouraging
  if (
    lowerText.includes('try') ||
    lowerText.includes('keep going') ||
    lowerText.includes('almost') ||
    lowerText.includes('close') ||
    lowerText.includes('good effort')
  ) {
    return 'encouraging';
  }

  // Thinking/pondering
  if (
    lowerText.includes('think about') ||
    lowerText.includes('consider') ||
    lowerText.includes('let me') ||
    lowerText.includes('interesting') ||
    lowerText.includes('hmm')
  ) {
    return 'thinking';
  }

  // Surprised
  if (
    lowerText.includes('wow') ||
    lowerText.includes('amazing') ||
    lowerText.includes('incredible') ||
    lowerText.includes('surprising')
  ) {
    return 'surprised';
  }

  // Questions often show curiosity/thinking
  if (lowerText.includes('?') || lowerText.includes('what do you think')) {
    return 'thinking';
  }

  return 'neutral';
}

// Generate visemes from text for lip-sync
function generateVisemesFromText(text: string): Array<{ time: number; viseme: string; duration: number }> {
  const visemeMap: Record<string, string> = {
    a: 'aa',
    e: 'E',
    i: 'I',
    o: 'O',
    u: 'U',
    b: 'PP',
    m: 'PP',
    p: 'PP',
    f: 'FF',
    v: 'FF',
    d: 'DD',
    t: 'DD',
    n: 'DD',
    s: 'SS',
    z: 'SS',
    r: 'RR',
    l: 'RR',
    k: 'kk',
    g: 'kk',
    w: 'O',
    y: 'I',
  };

  const visemes: Array<{ time: number; viseme: string; duration: number }> = [];
  const charsPerSecond = 14; // Average speaking speed
  let timeOffset = 0;

  const textLower = text.toLowerCase();

  for (let i = 0; i < textLower.length; i++) {
    const char = textLower[i];

    if (visemeMap[char]) {
      visemes.push({
        time: timeOffset,
        viseme: visemeMap[char],
        duration: 0.07,
      });
    } else if (char === ' ') {
      visemes.push({
        time: timeOffset,
        viseme: 'sil',
        duration: 0.05,
      });
    }

    timeOffset += 1 / charsPerSecond;
  }

  return visemes;
}

export function useAvatarSpeech(options: UseAvatarSpeechOptions = {}) {
  const { enabled = true, emotionDetection = true } = options;
  const { client, connected, volume } = useLiveAPIContext();
  const { speak, setEmotion, state, currentAvatar } = useAvatarContext();

  const lastTextRef = useRef<string>('');
  const audioAnalyzerRef = useRef<AnalyserNode | null>(null);
  const isSpeakingRef = useRef<boolean>(false);

  // Track when AI is speaking based on volume
  useEffect(() => {
    if (!enabled || !connected) return;

    // When volume is detected, avatar should be speaking
    const speaking = volume > 0.01;

    if (speaking !== isSpeakingRef.current) {
      isSpeakingRef.current = speaking;

      // Dispatch event for avatar components
      window.dispatchEvent(
        new CustomEvent('avatar-speaking', {
          detail: { speaking, volume },
        })
      );
    }
  }, [volume, enabled, connected]);

  // Handle text responses from Gemini
  const handleTextResponse = useCallback(
    (text: string) => {
      if (!enabled || !currentAvatar) return;

      // Avoid processing the same text twice
      if (text === lastTextRef.current) return;
      lastTextRef.current = text;

      // Detect emotion from text
      if (emotionDetection) {
        const emotion = detectEmotion(text);
        setEmotion(emotion);
      }

      // Generate visemes for lip-sync
      const visemes = generateVisemesFromText(text);

      // Dispatch visemes for the avatar
      window.dispatchEvent(
        new CustomEvent('avatar-visemes', {
          detail: visemes,
        })
      );

      // Notify avatar context
      speak(text, detectEmotion(text));
    },
    [enabled, currentAvatar, emotionDetection, setEmotion, speak]
  );

  // Listen for text content from Gemini Live API
  useEffect(() => {
    if (!enabled || !client) return;

    const handleContent = (content: any) => {
      // Extract text from content
      if (content?.parts) {
        for (const part of content.parts) {
          if (part.text) {
            handleTextResponse(part.text);
          }
        }
      }
    };

    // Listen for model responses
    client.on('content', handleContent);

    return () => {
      client.off('content', handleContent);
    };
  }, [client, enabled, handleTextResponse]);

  // Provide audio level data for real-time lip-sync
  const sendAudioLevel = useCallback((level: number) => {
    window.dispatchEvent(
      new CustomEvent('avatar-audio-level', {
        detail: { level },
      })
    );
  }, []);

  return {
    isAvatarSpeaking: state.isSpeaking,
    currentEmotion: state.currentEmotion,
    sendAudioLevel,
    handleTextResponse,
  };
}

export default useAvatarSpeech;
