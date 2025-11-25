/**
 * VideoAvatar Component
 * Real talking avatar using actual photos with CSS-based lip-sync animation
 * Falls back gracefully when D-ID API is not available
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { ttsService, LipSyncData } from '../../services/TTSService';
import { didService } from '../../services/DIDService';
import { storageService } from '../../services/StorageService';
import './VideoAvatar.scss';

interface VideoAvatarProps {
  className?: string;
  size?: 'small' | 'medium' | 'large';
  showName?: boolean;
  onSpeakingStart?: () => void;
  onSpeakingEnd?: () => void;
}

const VideoAvatar: React.FC<VideoAvatarProps> = ({
  className = '',
  size = 'large',
  showName = true,
  onSpeakingStart,
  onSpeakingEnd,
}) => {
  const { currentAvatar, state } = useAvatarContext();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [mouthOpen, setMouthOpen] = useState(0);
  const [currentViseme, setCurrentViseme] = useState('sil');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [useVideoMode, setUseVideoMode] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [blinking, setBlinking] = useState(false);

  // Check for D-ID API availability
  useEffect(() => {
    const apiKeys = storageService.getApiKeys();
    if (apiKeys.did) {
      didService.setApiKey(apiKeys.did);
      setUseVideoMode(didService.hasApiKey());
    }
  }, []);

  // Set up TTS lip-sync callback
  useEffect(() => {
    ttsService.setLipSyncCallback((data: LipSyncData) => {
      setMouthOpen(data.mouthOpen);
      setCurrentViseme(data.viseme);
    });

    ttsService.setEventCallbacks(
      () => {
        setIsSpeaking(true);
        onSpeakingStart?.();
      },
      () => {
        setIsSpeaking(false);
        setMouthOpen(0);
        onSpeakingEnd?.();
      }
    );

    return () => {
      ttsService.setLipSyncCallback(null);
      ttsService.setEventCallbacks(null, null);
    };
  }, [onSpeakingStart, onSpeakingEnd]);

  // Listen for speak events from context
  useEffect(() => {
    const handleSpeak = (event: Event) => {
      const customEvent = event as CustomEvent<{ text: string; emotion?: string }>;
      if (currentAvatar && customEvent.detail?.text) {
        speak(customEvent.detail.text);
      }
    };

    window.addEventListener('avatar-speak', handleSpeak);
    return () => {
      window.removeEventListener('avatar-speak', handleSpeak);
    };
  }, [currentAvatar]);

  // Idle blinking animation
  useEffect(() => {
    if (isSpeaking) return;

    const blinkInterval = setInterval(() => {
      setBlinking(true);
      setTimeout(() => setBlinking(false), 150);
    }, 3000 + Math.random() * 2000);

    return () => clearInterval(blinkInterval);
  }, [isSpeaking]);

  // Speak function
  const speak = useCallback(async (text: string) => {
    if (!currentAvatar) return;

    if (useVideoMode && didService.hasApiKey()) {
      // Use D-ID for real video lip-sync
      const success = await didService.speak(text);
      if (!success) {
        // Fallback to TTS
        await ttsService.speakAsAvatar(text, currentAvatar.id);
      }
    } else {
      // Use Web Speech API with animated photo
      await ttsService.speakAsAvatar(text, currentAvatar.id);
    }
  }, [currentAvatar, useVideoMode]);

  // Expose speak function globally for other components
  useEffect(() => {
    (window as any).avatarSpeak = speak;
    return () => {
      delete (window as any).avatarSpeak;
    };
  }, [speak]);

  const dimensions = {
    small: 150,
    medium: 250,
    large: 350,
  };

  const avatarSize = dimensions[size];

  if (!currentAvatar) {
    return (
      <div className={`video-avatar ${className} ${size} placeholder`}>
        <div className="avatar-placeholder">
          <span className="material-symbols-outlined">person</span>
          <p>Select a tutor to begin</p>
        </div>
      </div>
    );
  }

  // Calculate mouth animation styles
  const mouthStyle = {
    transform: `scaleY(${1 + mouthOpen * 0.5}) scaleX(${1 + mouthOpen * 0.2})`,
    opacity: mouthOpen > 0.1 ? 1 : 0,
  };

  const eyeStyle = {
    transform: blinking ? 'scaleY(0.1)' : 'scaleY(1)',
    transition: 'transform 0.1s ease',
  };

  return (
    <div className={`video-avatar ${className} ${size} ${isSpeaking ? 'speaking' : ''}`}>
      <div
        className="avatar-container"
        style={{ width: avatarSize, height: avatarSize }}
      >
        {/* Video element for D-ID streaming (hidden when not using) */}
        {useVideoMode && (
          <video
            ref={videoRef}
            className={`avatar-video ${isStreaming ? 'active' : ''}`}
            autoPlay
            playsInline
          />
        )}

        {/* Photo-based avatar with CSS animation */}
        <div className={`avatar-photo-container ${useVideoMode && isStreaming ? 'hidden' : ''}`}>
          {currentAvatar.image && (
            <img
              src={currentAvatar.image}
              alt={currentAvatar.name}
              className="avatar-photo"
              onLoad={() => setImageLoaded(true)}
              onError={(e) => {
                // Fallback to initials
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          )}

          {/* Animated overlay for lip-sync */}
          {imageLoaded && (
            <div className="animation-overlay">
              {/* Mouth animation layer */}
              <div
                className={`mouth-overlay ${currentViseme}`}
                style={mouthStyle}
              >
                <div className="mouth-shape" />
              </div>

              {/* Eye blink overlay */}
              <div className="eyes-overlay" style={eyeStyle}>
                <div className="eye left" />
                <div className="eye right" />
              </div>

              {/* Speaking glow effect */}
              {isSpeaking && (
                <div className="speaking-glow" />
              )}
            </div>
          )}

          {/* Fallback initials if no image */}
          {!currentAvatar.image && (
            <div className="avatar-initials">
              {currentAvatar.name.split(' ').map(n => n[0]).join('')}
            </div>
          )}
        </div>

        {/* Speaking indicator waves */}
        {isSpeaking && (
          <div className="audio-waves">
            <div className="wave" style={{ animationDelay: '0ms' }} />
            <div className="wave" style={{ animationDelay: '100ms' }} />
            <div className="wave" style={{ animationDelay: '200ms' }} />
          </div>
        )}

        {/* Emotion indicator */}
        <div className={`emotion-indicator ${state.currentEmotion}`}>
          <span className="material-symbols-outlined">
            {state.currentEmotion === 'happy' ? 'sentiment_satisfied' :
             state.currentEmotion === 'thinking' ? 'psychology' :
             state.currentEmotion === 'encouraging' ? 'thumb_up' :
             state.currentEmotion === 'surprised' ? 'sentiment_excited' :
             'sentiment_neutral'}
          </span>
        </div>
      </div>

      {showName && (
        <div className="avatar-info">
          <h3 className="avatar-name">{currentAvatar.name}</h3>
          <span className="avatar-subject">{currentAvatar.subject}</span>
          {isSpeaking && <span className="speaking-badge">Speaking...</span>}
        </div>
      )}
    </div>
  );
};

export default VideoAvatar;
