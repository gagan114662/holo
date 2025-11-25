/**
 * TalkingAvatar Component
 * A 2D/2.5D animated avatar with lip-sync for educational tutoring
 * Uses CSS animations and canvas for smooth, performant animation
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useAvatarContext } from '../../contexts/AvatarContext';
import { AvatarEmotion, Viseme, EMOTION_BLEND_MAP } from './types';
import './TalkingAvatar.scss';

interface TalkingAvatarProps {
  className?: string;
  size?: 'small' | 'medium' | 'large';
  showName?: boolean;
}

// Viseme to mouth shape mapping for 2D animation
const MOUTH_SHAPES: Record<string, { width: number; height: number; shape: string }> = {
  sil: { width: 0.3, height: 0.1, shape: 'closed' },
  PP: { width: 0.1, height: 0.05, shape: 'pursed' },
  FF: { width: 0.4, height: 0.15, shape: 'teeth' },
  TH: { width: 0.35, height: 0.2, shape: 'tongue' },
  DD: { width: 0.3, height: 0.25, shape: 'open' },
  kk: { width: 0.25, height: 0.3, shape: 'back' },
  CH: { width: 0.2, height: 0.25, shape: 'rounded' },
  SS: { width: 0.35, height: 0.1, shape: 'teeth' },
  nn: { width: 0.3, height: 0.2, shape: 'open' },
  RR: { width: 0.25, height: 0.3, shape: 'rounded' },
  aa: { width: 0.5, height: 0.6, shape: 'wide' },
  E: { width: 0.45, height: 0.35, shape: 'smile' },
  I: { width: 0.4, height: 0.25, shape: 'smile' },
  O: { width: 0.35, height: 0.5, shape: 'rounded' },
  U: { width: 0.25, height: 0.4, shape: 'pursed' },
};

const TalkingAvatar: React.FC<TalkingAvatarProps> = ({
  className = '',
  size = 'large',
  showName = true,
}) => {
  const { currentAvatar, state } = useAvatarContext();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);
  const [currentViseme, setCurrentViseme] = useState<string>('sil');
  const [mouthOpen, setMouthOpen] = useState(0);
  const visemeQueueRef = useRef<Viseme[]>([]);
  const visemeStartTimeRef = useRef<number>(0);

  // Avatar dimensions based on size
  const dimensions = {
    small: { width: 150, height: 150 },
    medium: { width: 250, height: 250 },
    large: { width: 400, height: 400 },
  };

  const { width, height } = dimensions[size];

  // Handle incoming visemes for lip-sync
  useEffect(() => {
    const handleVisemes = (event: CustomEvent<Viseme[]>) => {
      visemeQueueRef.current = event.detail;
      visemeStartTimeRef.current = performance.now();
    };

    window.addEventListener('avatar-visemes', handleVisemes as EventListener);
    return () => {
      window.removeEventListener('avatar-visemes', handleVisemes as EventListener);
    };
  }, []);

  // Process viseme queue during speech
  useEffect(() => {
    if (!state.isSpeaking) {
      setCurrentViseme('sil');
      setMouthOpen(0);
      return;
    }

    const processVisemes = () => {
      const elapsed = (performance.now() - visemeStartTimeRef.current) / 1000;
      const queue = visemeQueueRef.current;

      // Find current viseme based on timing
      let activeViseme = 'sil';
      for (const v of queue) {
        if (elapsed >= v.time && elapsed < v.time + v.duration) {
          activeViseme = v.viseme;
          break;
        }
      }

      setCurrentViseme(activeViseme);

      // Calculate mouth openness
      const shape = MOUTH_SHAPES[activeViseme] || MOUTH_SHAPES.sil;
      setMouthOpen(shape.height);
    };

    const interval = setInterval(processVisemes, 50); // 20 FPS for visemes
    return () => clearInterval(interval);
  }, [state.isSpeaking]);

  // Draw the avatar
  const drawAvatar = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Get current emotion state
    const emotion = state.currentEmotion;

    // Draw background circle
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, width * 0.45, 0, Math.PI * 2);
    ctx.fillStyle = '#e8e0d5';
    ctx.fill();

    // Draw face based on avatar
    drawFace(ctx, width, height, emotion, currentViseme, mouthOpen);

    // Continue animation
    animationRef.current = requestAnimationFrame(drawAvatar);
  }, [width, height, state.currentEmotion, currentViseme, mouthOpen]);

  // Start animation loop
  useEffect(() => {
    animationRef.current = requestAnimationFrame(drawAvatar);
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [drawAvatar]);

  // Idle animation - subtle movements
  useEffect(() => {
    if (state.isSpeaking) return;

    const idleAnimation = () => {
      // Subtle blink every 3-5 seconds
      const blinkInterval = setInterval(() => {
        // Trigger blink animation via state
      }, 3000 + Math.random() * 2000);

      return () => clearInterval(blinkInterval);
    };

    return idleAnimation();
  }, [state.isSpeaking]);

  if (!currentAvatar) {
    return (
      <div className={`talking-avatar ${className} ${size} placeholder`}>
        <div className="avatar-placeholder">
          <span className="material-symbols-outlined">person</span>
          <p>Select an avatar to begin</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`talking-avatar ${className} ${size}`}>
      <div className="avatar-container">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className="avatar-canvas"
        />

        {/* Speaking indicator */}
        {state.isSpeaking && (
          <div className="speaking-indicator">
            <div className="wave"></div>
            <div className="wave"></div>
            <div className="wave"></div>
          </div>
        )}

        {/* Emotion indicator */}
        <div className={`emotion-glow ${state.currentEmotion}`} />
      </div>

      {showName && (
        <div className="avatar-info">
          <h3 className="avatar-name">{currentAvatar.name}</h3>
          <span className="avatar-subject">{currentAvatar.subject}</span>
        </div>
      )}
    </div>
  );
};

// Helper function to draw the face
function drawFace(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  emotion: AvatarEmotion,
  viseme: string,
  mouthOpen: number
) {
  const centerX = width / 2;
  const centerY = height / 2;
  const faceRadius = width * 0.4;

  // Face base
  ctx.beginPath();
  ctx.arc(centerX, centerY, faceRadius, 0, Math.PI * 2);
  ctx.fillStyle = '#f5e6d3';
  ctx.fill();
  ctx.strokeStyle = '#d4c4b0';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Eyes
  const eyeY = centerY - faceRadius * 0.15;
  const eyeSpacing = faceRadius * 0.35;
  const eyeRadius = faceRadius * 0.12;

  // Left eye
  drawEye(ctx, centerX - eyeSpacing, eyeY, eyeRadius, emotion);
  // Right eye
  drawEye(ctx, centerX + eyeSpacing, eyeY, eyeRadius, emotion);

  // Eyebrows based on emotion
  drawEyebrows(ctx, centerX, eyeY - eyeRadius * 1.8, eyeSpacing, emotion);

  // Nose
  ctx.beginPath();
  ctx.moveTo(centerX, centerY - faceRadius * 0.05);
  ctx.lineTo(centerX - faceRadius * 0.08, centerY + faceRadius * 0.15);
  ctx.lineTo(centerX + faceRadius * 0.08, centerY + faceRadius * 0.15);
  ctx.strokeStyle = '#c9a88a';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Mouth based on viseme and emotion
  const mouthY = centerY + faceRadius * 0.35;
  drawMouth(ctx, centerX, mouthY, faceRadius, viseme, mouthOpen, emotion);
}

function drawEye(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  emotion: AvatarEmotion
) {
  // Eye white
  ctx.beginPath();
  ctx.ellipse(x, y, radius, radius * 0.8, 0, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff';
  ctx.fill();
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 1;
  ctx.stroke();

  // Iris
  const irisRadius = radius * 0.6;
  ctx.beginPath();
  ctx.arc(x, y, irisRadius, 0, Math.PI * 2);
  ctx.fillStyle = '#4a3728';
  ctx.fill();

  // Pupil
  const pupilRadius = irisRadius * 0.5;
  ctx.beginPath();
  ctx.arc(x, y, pupilRadius, 0, Math.PI * 2);
  ctx.fillStyle = '#1a1a1a';
  ctx.fill();

  // Eye highlight
  ctx.beginPath();
  ctx.arc(x - pupilRadius * 0.3, y - pupilRadius * 0.3, pupilRadius * 0.3, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff';
  ctx.fill();

  // Squint for happy emotion
  if (emotion === 'happy') {
    ctx.beginPath();
    ctx.arc(x, y - radius * 0.2, radius, 0.1 * Math.PI, 0.9 * Math.PI);
    ctx.fillStyle = '#f5e6d3';
    ctx.fill();
  }

  // Wide eyes for surprised
  if (emotion === 'surprised') {
    ctx.beginPath();
    ctx.ellipse(x, y, radius * 1.2, radius * 1.1, 0, 0, Math.PI * 2);
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}

function drawEyebrows(
  ctx: CanvasRenderingContext2D,
  centerX: number,
  y: number,
  spacing: number,
  emotion: AvatarEmotion
) {
  ctx.strokeStyle = '#5a4a3a';
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';

  const browLength = spacing * 0.6;

  // Left eyebrow
  ctx.beginPath();
  let leftStart = { x: centerX - spacing - browLength / 2, y: y };
  let leftEnd = { x: centerX - spacing + browLength / 2, y: y };

  // Adjust based on emotion
  if (emotion === 'sad') {
    leftStart.y -= 5;
    leftEnd.y += 5;
  } else if (emotion === 'surprised') {
    leftStart.y -= 10;
    leftEnd.y -= 10;
  } else if (emotion === 'thinking') {
    leftEnd.y -= 8;
  } else if (emotion === 'confused') {
    leftStart.y += 5;
    leftEnd.y -= 5;
  }

  ctx.moveTo(leftStart.x, leftStart.y);
  ctx.lineTo(leftEnd.x, leftEnd.y);
  ctx.stroke();

  // Right eyebrow (mirrored)
  ctx.beginPath();
  let rightStart = { x: centerX + spacing - browLength / 2, y: y };
  let rightEnd = { x: centerX + spacing + browLength / 2, y: y };

  if (emotion === 'sad') {
    rightStart.y += 5;
    rightEnd.y -= 5;
  } else if (emotion === 'surprised') {
    rightStart.y -= 10;
    rightEnd.y -= 10;
  } else if (emotion === 'thinking') {
    rightStart.y -= 8;
  } else if (emotion === 'confused') {
    rightStart.y -= 5;
    rightEnd.y += 5;
  }

  ctx.moveTo(rightStart.x, rightStart.y);
  ctx.lineTo(rightEnd.x, rightEnd.y);
  ctx.stroke();
}

function drawMouth(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  faceRadius: number,
  viseme: string,
  mouthOpen: number,
  emotion: AvatarEmotion
) {
  const shape = MOUTH_SHAPES[viseme] || MOUTH_SHAPES.sil;
  const baseWidth = faceRadius * 0.4;
  const baseHeight = faceRadius * 0.15;

  const mouthWidth = baseWidth * (0.5 + shape.width);
  const mouthHeight = baseHeight * (0.3 + mouthOpen * 3);

  ctx.beginPath();

  if (emotion === 'happy' || shape.shape === 'smile') {
    // Smiling mouth
    ctx.moveTo(x - mouthWidth / 2, y);
    ctx.quadraticCurveTo(x, y + mouthHeight * 1.5, x + mouthWidth / 2, y);
    if (mouthOpen > 0.2) {
      ctx.quadraticCurveTo(x, y + mouthHeight * 0.5, x - mouthWidth / 2, y);
      ctx.fillStyle = '#8b4513';
      ctx.fill();
    }
    ctx.strokeStyle = '#8b4513';
    ctx.lineWidth = 2;
    ctx.stroke();
  } else if (shape.shape === 'rounded' || shape.shape === 'pursed') {
    // O or U shape
    ctx.ellipse(x, y, mouthWidth * 0.4, mouthHeight, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#8b4513';
    ctx.fill();
  } else if (mouthOpen > 0.3) {
    // Open mouth
    ctx.ellipse(x, y, mouthWidth / 2, mouthHeight, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#4a1c1c';
    ctx.fill();

    // Teeth hint for wide open
    if (mouthOpen > 0.5) {
      ctx.beginPath();
      ctx.rect(x - mouthWidth / 3, y - mouthHeight / 2, mouthWidth * 0.66, mouthHeight * 0.4);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
    }
  } else {
    // Neutral/closed mouth
    ctx.moveTo(x - mouthWidth / 2, y);
    ctx.lineTo(x + mouthWidth / 2, y);
    ctx.strokeStyle = '#8b4513';
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  // Sad mouth override
  if (emotion === 'sad') {
    ctx.beginPath();
    ctx.moveTo(x - mouthWidth / 2, y + 5);
    ctx.quadraticCurveTo(x, y - mouthHeight, x + mouthWidth / 2, y + 5);
    ctx.strokeStyle = '#8b4513';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}

export default TalkingAvatar;
