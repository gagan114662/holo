/**
 * AvatarCreator Component
 * Create custom avatars from uploaded photos - SUPERIOR to 2wai
 * 2wai requires 3 minutes + app, we do it instantly in browser
 */

import React, { useState, useRef, useCallback } from 'react';
import './AvatarCreator.scss';

interface AvatarCreatorProps {
  isOpen: boolean;
  onAvatarCreated: (avatar: CustomAvatar) => void;
  onClose: () => void;
}

export interface CustomAvatar {
  id: string;
  name: string;
  photo: string;
  subject: string;
  personality: string;
  voiceId: string;
  greeting: string;
  createdAt: Date;
}

const VOICE_OPTIONS = [
  { id: 'en-US-Standard-A', name: 'Allison (Female)', lang: 'English' },
  { id: 'en-US-Standard-D', name: 'David (Male)', lang: 'English' },
  { id: 'en-GB-Standard-A', name: 'Emma (Female, British)', lang: 'English' },
  { id: 'en-GB-Standard-B', name: 'James (Male, British)', lang: 'English' },
  { id: 'es-US-Standard-A', name: 'Sofia (Female)', lang: 'Spanish' },
  { id: 'fr-FR-Standard-A', name: 'Marie (Female)', lang: 'French' },
  { id: 'de-DE-Standard-A', name: 'Anna (Female)', lang: 'German' },
  { id: 'ja-JP-Standard-A', name: 'Yuki (Female)', lang: 'Japanese' },
  { id: 'zh-CN-Standard-A', name: 'Li (Female)', lang: 'Chinese' },
];

const SUBJECT_OPTIONS = [
  'Mathematics', 'Physics', 'Chemistry', 'Biology',
  'Literature', 'History', 'Geography', 'Computer Science',
  'Art', 'Music', 'Philosophy', 'Economics',
  'Language Arts', 'Physical Education', 'Other'
];

const PERSONALITY_TEMPLATES = [
  { id: 'encouraging', name: 'Encouraging & Patient', desc: 'Supportive, celebrates small wins' },
  { id: 'socratic', name: 'Socratic Method', desc: 'Asks guiding questions' },
  { id: 'direct', name: 'Direct & Clear', desc: 'Straightforward explanations' },
  { id: 'playful', name: 'Playful & Fun', desc: 'Uses humor and games' },
  { id: 'challenging', name: 'Challenging', desc: 'Pushes students to excel' },
];

const AvatarCreator: React.FC<AvatarCreatorProps> = ({ isOpen, onAvatarCreated, onClose }) => {
  const [step, setStep] = useState(1);
  const [photo, setPhoto] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [subject, setSubject] = useState('');
  const [personality, setPersonality] = useState('encouraging');
  const [customPersonality, setCustomPersonality] = useState('');
  const [voiceId, setVoiceId] = useState('en-US-Standard-A');
  const [greeting, setGreeting] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isCameraMode, setIsCameraMode] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setPhoto(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Start camera for selfie
  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 }
      });
      setStream(mediaStream);
      setIsCameraMode(true);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      alert('Could not access camera. Please upload a photo instead.');
    }
  };

  // Capture photo from camera
  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        ctx.drawImage(videoRef.current, 0, 0);
        setPhoto(canvasRef.current.toDataURL('image/jpeg'));
        stopCamera();
      }
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsCameraMode(false);
  };

  // Generate default greeting based on name and subject
  const generateGreeting = useCallback(() => {
    if (name && subject) {
      const greetings = [
        `Hello! I'm ${name}, and I'm excited to help you learn ${subject}. What would you like to explore today?`,
        `Welcome! I'm ${name}, your ${subject} tutor. Let's discover something amazing together!`,
        `Hi there! I'm ${name}. Ready to dive into ${subject}? I'm here to guide you every step of the way.`,
      ];
      setGreeting(greetings[Math.floor(Math.random() * greetings.length)]);
    }
  }, [name, subject]);

  // Create the avatar
  const handleCreate = async () => {
    if (!photo || !name || !subject) return;

    setIsProcessing(true);

    // Simulate processing (in production, this would call an API)
    await new Promise(resolve => setTimeout(resolve, 1500));

    const newAvatar: CustomAvatar = {
      id: `custom_${Date.now()}`,
      name,
      photo,
      subject,
      personality: customPersonality || PERSONALITY_TEMPLATES.find(p => p.id === personality)?.desc || '',
      voiceId,
      greeting: greeting || `Hello! I'm ${name}, your ${subject} tutor.`,
      createdAt: new Date(),
    };

    setIsProcessing(false);
    onAvatarCreated(newAvatar);
  };

  const canProceed = () => {
    switch (step) {
      case 1: return !!photo;
      case 2: return !!name && !!subject;
      case 3: return true;
      case 4: return true;
      default: return false;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="avatar-creator-overlay" onClick={onClose}>
      <div className="avatar-creator" onClick={e => e.stopPropagation()}>
        <div className="creator-header">
          <h2>Create Your AI Tutor</h2>
          <p>Build a custom avatar in seconds - no app required!</p>
          <button className="close-btn" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Progress Steps */}
        <div className="step-indicator">
          {[1, 2, 3, 4].map(s => (
            <div key={s} className={`step ${step >= s ? 'active' : ''} ${step === s ? 'current' : ''}`}>
              <span className="step-number">{s}</span>
              <span className="step-label">
                {s === 1 ? 'Photo' : s === 2 ? 'Details' : s === 3 ? 'Personality' : 'Review'}
              </span>
            </div>
          ))}
        </div>

        <div className="creator-content">
          {/* Step 1: Photo Upload */}
          {step === 1 && (
            <div className="step-content photo-step">
              <h3>Add a Photo</h3>
              <p>Upload a photo or take a selfie to create your avatar's appearance</p>

              {!isCameraMode ? (
                <div className="photo-options">
                  {photo ? (
                    <div className="photo-preview">
                      <img src={photo} alt="Avatar preview" />
                      <button className="remove-photo" onClick={() => setPhoto(null)}>
                        <span className="material-symbols-outlined">delete</span>
                        Remove
                      </button>
                    </div>
                  ) : (
                    <>
                      <button className="upload-btn" onClick={() => fileInputRef.current?.click()}>
                        <span className="material-symbols-outlined">upload</span>
                        Upload Photo
                      </button>
                      <button className="camera-btn" onClick={startCamera}>
                        <span className="material-symbols-outlined">photo_camera</span>
                        Take Selfie
                      </button>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleFileUpload}
                        hidden
                      />
                    </>
                  )}
                </div>
              ) : (
                <div className="camera-view">
                  <video ref={videoRef} autoPlay playsInline muted />
                  <canvas ref={canvasRef} hidden />
                  <div className="camera-controls">
                    <button className="capture-btn" onClick={capturePhoto}>
                      <span className="material-symbols-outlined">camera</span>
                    </button>
                    <button className="cancel-btn" onClick={stopCamera}>Cancel</button>
                  </div>
                </div>
              )}

              <div className="photo-tips">
                <span className="material-symbols-outlined">tips_and_updates</span>
                <p>Tip: Use a clear, front-facing photo with good lighting for best results</p>
              </div>
            </div>
          )}

          {/* Step 2: Basic Details */}
          {step === 2 && (
            <div className="step-content details-step">
              <h3>Tutor Details</h3>

              <div className="form-group">
                <label>Tutor Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="e.g., Professor Smith, Coach Mike"
                />
              </div>

              <div className="form-group">
                <label>Subject</label>
                <select value={subject} onChange={e => setSubject(e.target.value)}>
                  <option value="">Select a subject...</option>
                  {SUBJECT_OPTIONS.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Voice</label>
                <div className="voice-options">
                  {VOICE_OPTIONS.map(voice => (
                    <button
                      key={voice.id}
                      className={`voice-option ${voiceId === voice.id ? 'selected' : ''}`}
                      onClick={() => setVoiceId(voice.id)}
                    >
                      <span className="voice-name">{voice.name}</span>
                      <span className="voice-lang">{voice.lang}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Personality */}
          {step === 3 && (
            <div className="step-content personality-step">
              <h3>Teaching Style</h3>

              <div className="personality-options">
                {PERSONALITY_TEMPLATES.map(p => (
                  <button
                    key={p.id}
                    className={`personality-option ${personality === p.id ? 'selected' : ''}`}
                    onClick={() => { setPersonality(p.id); setCustomPersonality(''); }}
                  >
                    <span className="personality-name">{p.name}</span>
                    <span className="personality-desc">{p.desc}</span>
                  </button>
                ))}
              </div>

              <div className="form-group">
                <label>Custom Personality (optional)</label>
                <textarea
                  value={customPersonality}
                  onChange={e => setCustomPersonality(e.target.value)}
                  placeholder="Describe how this tutor should behave, their tone, specific phrases they use..."
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label>
                  Greeting Message
                  <button className="generate-btn" onClick={generateGreeting}>
                    <span className="material-symbols-outlined">auto_awesome</span>
                    Generate
                  </button>
                </label>
                <textarea
                  value={greeting}
                  onChange={e => setGreeting(e.target.value)}
                  placeholder="What should the tutor say when a student starts learning?"
                  rows={2}
                />
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {step === 4 && (
            <div className="step-content review-step">
              <h3>Review Your Tutor</h3>

              <div className="avatar-preview-card">
                <div className="preview-photo">
                  {photo && <img src={photo} alt={name} />}
                </div>
                <div className="preview-details">
                  <h4>{name || 'Unnamed Tutor'}</h4>
                  <span className="preview-subject">{subject || 'No subject'}</span>
                  <p className="preview-personality">
                    {customPersonality || PERSONALITY_TEMPLATES.find(p => p.id === personality)?.desc}
                  </p>
                  <p className="preview-greeting">"{greeting}"</p>
                </div>
              </div>

              <div className="safety-notice">
                <span className="material-symbols-outlined">verified_user</span>
                <p>
                  <strong>Content Safety:</strong> All responses will be filtered for age-appropriate,
                  educational content. Your tutor will stay on-topic and follow classroom guidelines.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="creator-footer">
          {step > 1 && (
            <button className="back-btn" onClick={() => setStep(step - 1)}>
              <span className="material-symbols-outlined">arrow_back</span>
              Back
            </button>
          )}

          {step < 4 ? (
            <button
              className="next-btn"
              onClick={() => setStep(step + 1)}
              disabled={!canProceed()}
            >
              Next
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          ) : (
            <button
              className="create-btn"
              onClick={handleCreate}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <span className="material-symbols-outlined spinning">sync</span>
                  Creating...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined">check</span>
                  Create Tutor
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AvatarCreator;
