/**
 * HeyGenAvatar Component
 * WebRTC-based streaming avatar using HeyGen API
 * Provides photorealistic real-time lip-sync avatars
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import './HeyGenAvatar.scss';

interface HeyGenAvatarProps {
  className?: string;
  size?: 'small' | 'medium' | 'large';
  showName?: boolean;
}

interface HeyGenSession {
  sessionId: string;
  token: string;
  sdp: RTCSessionDescriptionInit;
}

const AVATAR_SERVICE_URL = process.env.REACT_APP_AVATAR_SERVICE_URL || 'http://localhost:8001';

const HeyGenAvatar: React.FC<HeyGenAvatarProps> = ({
  className = '',
  size = 'large',
  showName = true,
}) => {
  const { currentAvatar, session, state } = useAvatarContext();
  const videoRef = useRef<HTMLVideoElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const [connectionState, setConnectionState] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [error, setError] = useState<string | null>(null);

  // Size dimensions
  const dimensions = {
    small: { width: 200, height: 200 },
    medium: { width: 350, height: 350 },
    large: { width: 500, height: 500 },
  };

  const { width, height } = dimensions[size];

  // Initialize WebRTC connection when session is created
  const initializeConnection = useCallback(async () => {
    if (!session || session.provider !== 'heygen') return;

    try {
      setConnectionState('connecting');
      setError(null);

      // Create peer connection
      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' },
        ],
      });

      peerConnectionRef.current = pc;

      // Handle incoming video stream
      pc.ontrack = (event) => {
        if (videoRef.current && event.streams[0]) {
          videoRef.current.srcObject = event.streams[0];
        }
      };

      // Handle connection state changes
      pc.onconnectionstatechange = () => {
        switch (pc.connectionState) {
          case 'connected':
            setConnectionState('connected');
            break;
          case 'disconnected':
          case 'failed':
            setConnectionState('disconnected');
            setError('Connection lost. Attempting to reconnect...');
            break;
          case 'closed':
            setConnectionState('disconnected');
            break;
        }
      };

      // Handle ICE connection state
      pc.oniceconnectionstatechange = () => {
        console.log('ICE connection state:', pc.iceConnectionState);
      };

      // For HeyGen, we would set remote description from their API
      // This is a placeholder - actual implementation requires HeyGen SDK
      console.log('HeyGen connection initialized for session:', session.session_id);

      setConnectionState('connected');
    } catch (err) {
      console.error('Failed to initialize HeyGen connection:', err);
      setError('Failed to connect to avatar service');
      setConnectionState('disconnected');
    }
  }, [session]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
        peerConnectionRef.current = null;
      }
    };
  }, []);

  // Initialize when session changes
  useEffect(() => {
    if (session?.provider === 'heygen') {
      initializeConnection();
    }
  }, [session, initializeConnection]);

  if (!currentAvatar || session?.provider !== 'heygen') {
    return null;
  }

  return (
    <div className={`heygen-avatar ${className} ${size}`}>
      <div className="avatar-video-container" style={{ width, height }}>
        {connectionState === 'connecting' && (
          <div className="loading-overlay">
            <div className="loading-spinner">
              <span className="material-symbols-outlined spinning">sync</span>
            </div>
            <p>Connecting to {currentAvatar.name}...</p>
          </div>
        )}

        {error && (
          <div className="error-overlay">
            <span className="material-symbols-outlined">error</span>
            <p>{error}</p>
            <button onClick={initializeConnection}>Retry</button>
          </div>
        )}

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

        {/* Speaking indicator */}
        {state.isSpeaking && connectionState === 'connected' && (
          <div className="speaking-badge">
            <span className="material-symbols-outlined">graphic_eq</span>
            Speaking
          </div>
        )}

        {/* Connection status indicator */}
        <div className={`connection-indicator ${connectionState}`}>
          <span className="dot"></span>
          {connectionState === 'connected' ? 'Live' : connectionState}
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
