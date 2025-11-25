/**
 * AvatarSpeechHandler Component
 * Invisible component that handles the connection between
 * Gemini Live API audio/text and the avatar lip-sync system
 */

import React, { useEffect, useRef } from 'react';
import { useLiveAPIContext } from '../../contexts/LiveAPIContext';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { AvatarEmotion } from './types';

// Emotion detection from text content
function detectEmotionFromText(text: string): AvatarEmotion {
  const lowerText = text.toLowerCase();

  // Check for positive/encouraging phrases
  if (
    lowerText.includes('excellent') ||
    lowerText.includes('great job') ||
    lowerText.includes('perfect') ||
    lowerText.includes('correct') ||
    lowerText.includes('well done') ||
    lowerText.includes('that\'s right') ||
    lowerText.includes('exactly')
  ) {
    return 'happy';
  }

  // Encouraging when student is struggling
  if (
    lowerText.includes('try again') ||
    lowerText.includes('almost') ||
    lowerText.includes('close') ||
    lowerText.includes('keep trying') ||
    lowerText.includes('you can do it') ||
    lowerText.includes('good effort')
  ) {
    return 'encouraging';
  }

  // Thinking/pondering expressions
  if (
    lowerText.includes('let me think') ||
    lowerText.includes('consider') ||
    lowerText.includes('interesting') ||
    lowerText.includes('hmm') ||
    lowerText.includes('let\'s see')
  ) {
    return 'thinking';
  }

  // Surprised/impressed
  if (
    lowerText.includes('wow') ||
    lowerText.includes('amazing') ||
    lowerText.includes('incredible') ||
    lowerText.includes('impressive')
  ) {
    return 'surprised';
  }

  // Questions often accompany thinking
  if (text.includes('?')) {
    return 'thinking';
  }

  return 'neutral';
}

// Generate viseme timing from text
function generateVisemes(text: string): Array<{ time: number; viseme: string; duration: number }> {
  const PHONEME_TO_VISEME: Record<string, string> = {
    // Vowels
    'a': 'aa', 'e': 'E', 'i': 'I', 'o': 'O', 'u': 'U',
    // Bilabials
    'b': 'PP', 'm': 'PP', 'p': 'PP',
    // Labiodentals
    'f': 'FF', 'v': 'FF',
    // Dentals
    'd': 'DD', 't': 'DD', 'n': 'nn',
    // Alveolars
    's': 'SS', 'z': 'SS',
    // Post-alveolars
    'r': 'RR', 'l': 'RR',
    // Velars
    'k': 'kk', 'g': 'kk',
    // Approximants
    'w': 'O', 'y': 'I',
  };

  const visemes: Array<{ time: number; viseme: string; duration: number }> = [];
  const CHARS_PER_SECOND = 12; // Approximate speaking rate
  let currentTime = 0;

  for (let i = 0; i < text.length; i++) {
    const char = text[i].toLowerCase();

    if (PHONEME_TO_VISEME[char]) {
      visemes.push({
        time: currentTime,
        viseme: PHONEME_TO_VISEME[char],
        duration: 0.08,
      });
    } else if (char === ' ' || char === ',' || char === '.') {
      visemes.push({
        time: currentTime,
        viseme: 'sil',
        duration: char === '.' ? 0.15 : 0.05,
      });
    }

    currentTime += 1 / CHARS_PER_SECOND;
  }

  return visemes;
}

const AvatarSpeechHandler: React.FC = () => {
  const { client, connected, volume } = useLiveAPIContext();
  const { speak, setEmotion, currentAvatar, state } = useAvatarContext();

  const lastProcessedTextRef = useRef<string>('');
  const speakingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Monitor audio volume for speaking detection
  useEffect(() => {
    if (!connected || !currentAvatar) return;

    // When there's audio output, the avatar should be "speaking"
    const isSpeaking = volume > 0.02;

    // Dispatch speaking state change
    if (isSpeaking) {
      // Clear any existing timeout
      if (speakingTimeoutRef.current) {
        clearTimeout(speakingTimeoutRef.current);
      }

      window.dispatchEvent(
        new CustomEvent('avatar-speaking-state', {
          detail: { speaking: true, volume },
        })
      );

      // Set timeout to stop speaking after audio ends
      speakingTimeoutRef.current = setTimeout(() => {
        window.dispatchEvent(
          new CustomEvent('avatar-speaking-state', {
            detail: { speaking: false, volume: 0 },
          })
        );
      }, 300);
    }

    // Send audio level for real-time mouth movement
    window.dispatchEvent(
      new CustomEvent('avatar-audio-level', {
        detail: { level: volume },
      })
    );
  }, [volume, connected, currentAvatar]);

  // Handle text responses from Gemini for emotion and lip-sync
  useEffect(() => {
    if (!client || !currentAvatar) return;

    const handleServerContent = (content: any) => {
      // Extract text from server content
      let textContent = '';

      if (content?.modelTurn?.parts) {
        for (const part of content.modelTurn.parts) {
          if (part.text) {
            textContent += part.text;
          }
        }
      }

      if (!textContent || textContent === lastProcessedTextRef.current) {
        return;
      }

      lastProcessedTextRef.current = textContent;

      // Detect emotion from text
      const emotion = detectEmotionFromText(textContent);
      setEmotion(emotion);

      // Generate and dispatch visemes
      const visemes = generateVisemes(textContent);
      window.dispatchEvent(
        new CustomEvent('avatar-visemes', {
          detail: visemes,
        })
      );

      // Trigger speak in avatar context
      speak(textContent, emotion);
    };

    const handleTurnComplete = () => {
      // Reset when turn is complete
      lastProcessedTextRef.current = '';
      setEmotion('neutral');
    };

    client.on('content', handleServerContent);
    client.on('turncomplete', handleTurnComplete);

    return () => {
      client.off('content', handleServerContent);
      client.off('turncomplete', handleTurnComplete);
    };
  }, [client, currentAvatar, setEmotion, speak]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (speakingTimeoutRef.current) {
        clearTimeout(speakingTimeoutRef.current);
      }
    };
  }, []);

  // This component doesn't render anything visible
  return null;
};

export default AvatarSpeechHandler;
