/**
 * HeyGenAvatar Component
 * WebRTC-based streaming avatar using HeyGen API
 * Provides photorealistic real-time lip-sync avatars
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { heygenService, HeyGenSession } from '../../services/HeyGenService';
import { storageService } from '../../services/StorageService';
import './HeyGenAvatar.scss';

interface HeyGenAvatarProps {
  className?: string;
  size?: 'small' | 'medium' | 'large';
  showName?: boolean;
  quality?: 'low' | 'medium' | 'high';
  onReady?: () => void;
  onError?: (error: string) => void;
  onSpeakingChange?: (speaking: boolean) => void;
}

type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

// Map historical figures to HeyGen avatar IDs
// These would be actual HeyGen avatar IDs from your HeyGen account
const HEYGEN_AVATAR_MAP: Record<string, string> = {
  einstein: 'josh_lite3_20230714',      // Mature male avatar
  curie: 'anna_lite3_20230714',         // Female avatar
  shakespeare: 'wayne_lite3_20230714',   // Classic male avatar
  hypatia: 'angela_lite3_20230714',     // Female avatar
  darwin: 'tyler_lite3_20230714',       // Male avatar
  ada: 'lily_lite3_20230714',           // Female avatar
  socrates: 'josh_lite3_20230714',      // Mature male avatar
  frida: 'anna_lite3_20230714',         // Female avatar
  // New avatars from 2wai vision
  victoria: 'angela_lite3_20230714',    // Queen Victoria
  newton: 'wayne_lite3_20230714',       // Isaac Newton
  nightingale: 'lily_lite3_20230714',   // Florence Nightingale
  henry: 'josh_lite3_20230714',         // Henry VIII
};

// Voice mapping for historical figures
const HEYGEN_VOICE_MAP: Record<string, string> = {
  einstein: 'en-US-GuyNeural',
  curie: 'en-US-JennyNeural',
  shakespeare: 'en-GB-RyanNeural',
  hypatia: 'en-US-AriaNeural',
  darwin: 'en-GB-RyanNeural',
  ada: 'en-GB-SoniaNeural',
  socrates: 'en-US-GuyNeural',
  frida: 'es-MX-DaliaNeural',
  victoria: 'en-GB-SoniaNeural',
  newton: 'en-GB-RyanNeural',
  nightingale: 'en-GB-SoniaNeural',
  henry: 'en-GB-RyanNeural',
};

const HeyGenAvatar: React.FC<HeyGenAvatarProps> = ({
  className = '',
  size = 'large',
  showName = true,
  quality = 'medium',
  onReady,
  onError,
  onSpeakingChange,
}) => {
  const { currentAvatar, session, state } = useAvatarContext();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [heygenSession, setHeygenSession] = useState<HeyGenSession | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Size dimensions
  const dimensions = {
    small: { width: 200, height: 200 },
    medium: { width: 350, height: 350 },
    large: { width: 500, height: 500 },
  };

  const { width, height } = dimensions[size];

  // Check for API key on mount
  useEffect(() => {
    const apiKeys = storageService.getApiKeys();
    if (apiKeys.heygen) {
      heygenService.setApiKey(apiKeys.heygen);
    }
  }, []);

  // Set up service callbacks
  useEffect(() => {
    heygenService.setStateChangeCallback((state) => {
      setConnectionState(state);
      if (state === 'connected') {
        onReady?.();
      } else if (state === 'error') {
        onError?.('Connection error');
      }
    });

    heygenService.setSpeakingChangeCallback((speaking) => {
      setIsSpeaking(speaking);
      onSpeakingChange?.(speaking);
    });

    return () => {
      heygenService.setStateChangeCallback(null);
      heygenService.setSpeakingChangeCallback(null);
    };
  }, [onReady, onError, onSpeakingChange]);

  // Initialize HeyGen connection when avatar is selected
  const initializeConnection = useCallback(async () => {
    if (!currentAvatar || !heygenService.hasApiKey()) {
      setError('HeyGen API key not configured');
      return;
    }

    try {
      setConnectionState('connecting');
      setError(null);

      // Get the HeyGen avatar ID for this historical figure
      const heygenAvatarId = HEYGEN_AVATAR_MAP[currentAvatar.id] || 'josh_lite3_20230714';
      const voiceId = HEYGEN_VOICE_MAP[currentAvatar.id] || 'en-US-GuyNeural';

      // Create streaming session
      const newSession = await heygenService.createStreamingSession({
        quality,
        avatar_id: heygenAvatarId,
        voice_id: voiceId,
        background: {
          type: 'transparent',
        },
      });

      if (!newSession) {
        throw new Error('Failed to create HeyGen session');
      }

      setHeygenSession(newSession);

      // Start the session with video element
      if (videoRef.current) {
        const success = await heygenService.startSession(newSession, videoRef.current);
        if (!success) {
          throw new Error('Failed to start HeyGen stream');
        }
      }

      setIsInitialized(true);
      setConnectionState('connected');

      // Speak the avatar's greeting
      if (currentAvatar.greeting) {
        setTimeout(() => {
          heygenService.speak(currentAvatar.greeting);
        }, 1000);
      }
    } catch (err) {
      console.error('Failed to initialize HeyGen connection:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect to avatar service');
      setConnectionState('error');
      onError?.(err instanceof Error ? err.message : 'Connection failed');
    }
  }, [currentAvatar, quality, onError]);

  // Listen for speak events
  useEffect(() => {
    const handleSpeak = async (event: Event) => {
      const customEvent = event as CustomEvent<{ text: string; emotion?: string }>;
      if (customEvent.detail?.text && heygenService.isConnected()) {
        await heygenService.speak(customEvent.detail.text);
      }
    };

    window.addEventListener('heygen-speak', handleSpeak);
    window.addEventListener('avatar-speak', handleSpeak);

    return () => {
      window.removeEventListener('heygen-speak', handleSpeak);
      window.removeEventListener('avatar-speak', handleSpeak);
    };
  }, []);

  // Initialize when avatar changes and provider is heygen
  useEffect(() => {
    if (currentAvatar && session?.provider === 'heygen' && !isInitialized) {
      initializeConnection();
    }
  }, [currentAvatar, session, isInitialized, initializeConnection]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      heygenService.closeSession();
    };
  }, []);

  // Expose speak function globally
  useEffect(() => {
    (window as any).heygenSpeak = async (text: string) => {
      if (heygenService.isConnected()) {
        return heygenService.speak(text);
      }
      return false;
    };

    (window as any).heygenInterrupt = async () => {
      return heygenService.interrupt();
    };

    return () => {
      delete (window as any).heygenSpeak;
      delete (window as any).heygenInterrupt;
    };
  }, []);

  // Don't render if no avatar or wrong provider
  if (!currentAvatar || (session?.provider !== 'heygen' && heygenService.hasApiKey() === false)) {
    return null;
  }

  return (
    <div className={`heygen-avatar ${className} ${size}`}>
      <div
        className={`avatar-video-container ${connectionState}`}
        style={{ width, height }}
      >
        {connectionState === 'connecting' && (
          <div className="loading-overlay">
            <div className="loading-spinner">
              <span className="material-symbols-outlined spinning">sync</span>
            </div>
            <p>Connecting to {currentAvatar.name}...</p>
            <p style={{ fontSize: '12px', opacity: 0.7, marginTop: '8px' }}>
              Establishing secure video stream...
            </p>
          </div>
        )}

        {(connectionState === 'error' || error) && (
          <div className="error-overlay">
            <span className="material-symbols-outlined">error</span>
            <p>{error || 'Connection error'}</p>
            <button onClick={() => {
              setIsInitialized(false);
              setError(null);
              initializeConnection();
            }}>
              Retry Connection
            </button>
          </div>
        )}

        {/* Provider badge */}
        <div className="provider-badge">HeyGen</div>

        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted={false}
          className="avatar-video"
          style={{
            opacity: connectionState === 'connected' ? 1 : 0.3,
          }}
        />

        {/* Audio visualizer when speaking */}
        {isSpeaking && connectionState === 'connected' && (
          <div className="audio-visualizer">
            <div className="bar" />
            <div className="bar" />
            <div className="bar" />
            <div className="bar" />
            <div className="bar" />
          </div>
        )}

        {/* Speaking indicator */}
        {(isSpeaking || state.isSpeaking) && connectionState === 'connected' && (
          <div className="speaking-badge">
            <span className="material-symbols-outlined">graphic_eq</span>
            Speaking
          </div>
        )}

        {/* Connection status indicator */}
        <div className={`connection-indicator ${connectionState}`}>
          <span className="dot"></span>
          {connectionState === 'connected' ? 'Live' :
           connectionState === 'connecting' ? 'Connecting' :
           connectionState === 'error' ? 'Error' : 'Offline'}
        </div>

        {/* Quality selector */}
        <div className="quality-selector">
          {(['low', 'medium', 'high'] as const).map((q) => (
            <button
              key={q}
              className={quality === q ? 'active' : ''}
              onClick={() => {
                // Would need to reconnect with new quality
                console.log('Quality change to:', q);
              }}
              title={`${q} quality`}
            >
              {q[0].toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {showName && currentAvatar && (
        <div className="avatar-info">
          <h3>{currentAvatar.name}</h3>
          <span className="subject">{currentAvatar.subject}</span>
        </div>
      )}
    </div>
  );
};

export default HeyGenAvatar;
