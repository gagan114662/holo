/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { useRef, useState, useEffect } from "react";
import "./App.scss";
import { LiveAPIProvider } from "./contexts/LiveAPIContext";
import { AvatarContextProvider, useAvatarContext } from "./contexts/AvatarContext";
import SidePanel from "./components/side-panel/SidePanel";
import MediaMixerDisplay from "./components/media-mixer-display/MediaMixerDisplay";
import ScratchpadCapture from "./components/scratchpad-capture/ScratchpadCapture";
import QuestionDisplay from "./components/question-display/QuestionDisplay";
import ControlTray from "./components/control-tray/ControlTray";
import { VideoAvatar, AvatarSelector, AvatarSpeechHandler } from "./components/avatar";
import { AnswerInput } from "./components/answer-input";
import { ProgressDashboard } from "./components/progress-dashboard";
import { LanguageSelector, Language } from "./components/language-selector";
import { AvatarCreator, CustomAvatar } from "./components/avatar-creator";
import { TeacherDashboard } from "./components/teacher-dashboard";
import { ErrorBoundary } from "./components/error-boundary";
import { storageService } from "./services/StorageService";
import cn from "classnames";
import { LiveClientOptions } from "./types";
import Scratchpad from "./components/scratchpad/Scratchpad";

const API_KEY = process.env.REACT_APP_GEMINI_API_KEY as string;
if (typeof API_KEY !== "string") {
  throw new Error("set REACT_APP_GEMINI_API_KEY in .env");
}

const apiOptions: LiveClientOptions = {
  apiKey: API_KEY,
};

type AppView = 'selector' | 'tutoring';

// Tutoring Interface Component (extracted for useAvatarContext access)
function TutoringInterface({
  socket,
  onBack,
}: {
  socket: WebSocket | null;
  onBack: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const renderCanvasRef = useRef<HTMLCanvasElement>(null);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [mixerStream, setMixerStream] = useState<MediaStream | null>(null);
  const mixerVideoRef = useRef<HTMLVideoElement>(null);
  const [isScratchpadOpen, setScratchpadOpen] = useState(false);
  const [isAvatarMinimized, setAvatarMinimized] = useState(false);
  const [isProgressOpen, setProgressOpen] = useState(false);
  const [isTeacherDashboardOpen, setTeacherDashboardOpen] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [currentSubject, setCurrentSubject] = useState('general');

  const { currentAvatar } = useAvatarContext();

  // Start session when entering tutoring view
  useEffect(() => {
    if (currentAvatar) {
      const subject = currentAvatar.subject || 'general';
      setCurrentSubject(subject);
      storageService.startSession(currentAvatar.id, currentAvatar.name, subject);
    }

    // End session when leaving
    return () => {
      storageService.endSession();
    };
  }, [currentAvatar]);

  useEffect(() => {
    if (mixerVideoRef.current && mixerStream) {
      mixerVideoRef.current.srcObject = mixerStream;
    }
  }, [mixerStream]);

  const handleLanguageChange = (language: Language) => {
    setCurrentLanguage(language.code);
    console.log(`Language changed to: ${language.name}`);
  };

  return (
    <div className="streaming-console">
      <SidePanel />
      <main>
        {/* Top bar with controls */}
        <div className="top-bar">
          <div className="top-bar-left">
            <button className="back-button" onClick={onBack}>
              <span className="material-symbols-outlined">arrow_back</span>
              Change Tutor
            </button>
          </div>

          <div className="top-bar-center">
            {currentAvatar && (
              <span className="current-tutor">
                Learning with <strong>{currentAvatar.name}</strong>
              </span>
            )}
          </div>

          <div className="top-bar-right">
            <LanguageSelector
              currentLanguage={currentLanguage}
              onLanguageChange={handleLanguageChange}
              compact
            />
            <button
              className="icon-button"
              onClick={() => setProgressOpen(true)}
              title="View Progress"
            >
              <span className="material-symbols-outlined">insights</span>
            </button>
            <button
              className="icon-button teacher-btn"
              onClick={() => setTeacherDashboardOpen(true)}
              title="Teacher Dashboard"
            >
              <span className="material-symbols-outlined">school</span>
            </button>
            <button
              className={cn("icon-button", { active: isAvatarMinimized })}
              onClick={() => setAvatarMinimized(!isAvatarMinimized)}
            >
              <span className="material-symbols-outlined">
                {isAvatarMinimized ? "open_in_full" : "close_fullscreen"}
              </span>
            </button>
          </div>
        </div>

        <div className="main-app-area">
          {/* Avatar Display */}
          <div className={cn("avatar-panel", { minimized: isAvatarMinimized })}>
            <VideoAvatar
              size={isAvatarMinimized ? "small" : "large"}
              showName={!isAvatarMinimized}
            />
          </div>

          {/* Question, Answer Input, and Scratchpad */}
          <div className="question-panel">
            <ScratchpadCapture socket={socket}>
              <QuestionDisplay />
              {/* Answer Input - KEY FEATURE */}
              <AnswerInput
                questionType="free_text"
                subject={currentSubject}
                skill={currentSubject}
                onSubmit={(answer, isCorrect) => {
                  console.log('Answer:', answer, 'Correct:', isCorrect);
                  // Refresh progress data after each answer
                }}
              />
              {isScratchpadOpen && (
                <div className="scratchpad-container">
                  <Scratchpad />
                </div>
              )}
            </ScratchpadCapture>
          </div>

          {/* Media Mixer */}
          <MediaMixerDisplay socket={socket} renderCanvasRef={renderCanvasRef} />
        </div>

        <ControlTray
          socket={socket}
          renderCanvasRef={renderCanvasRef}
          videoRef={videoRef}
          supportsVideo={true}
          onVideoStreamChange={setVideoStream}
          onMixerStreamChange={setMixerStream}
          enableEditingSettings={true}
        >
          <button onClick={() => setScratchpadOpen(!isScratchpadOpen)}>
            <span className="material-symbols-outlined">
              {isScratchpadOpen ? "close" : "edit"}
            </span>
          </button>
        </ControlTray>

        {/* Progress Dashboard Modal */}
        <ProgressDashboard isOpen={isProgressOpen} onClose={() => setProgressOpen(false)} />

        {/* Teacher Dashboard Modal */}
        <TeacherDashboard
          isOpen={isTeacherDashboardOpen}
          onClose={() => setTeacherDashboardOpen(false)}
        />
      </main>
    </div>
  );
}

function App() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [currentView, setCurrentView] = useState<AppView>('selector');
  const [showAvatarCreator, setShowAvatarCreator] = useState(false);
  const [customAvatars, setCustomAvatars] = useState<CustomAvatar[]>([]);

  const handleAvatarCreated = (avatar: CustomAvatar) => {
    setCustomAvatars(prev => [...prev, avatar]);
    setShowAvatarCreator(false);
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    ws.onerror = () => console.log('Media mixer not available');
    setSocket(ws);
    return () => ws.close();
  }, []);

  return (
    <ErrorBoundary>
      <div className="App">
        <LiveAPIProvider options={apiOptions}>
          <AvatarContextProvider>
            <AvatarSpeechHandler />

            {currentView === 'selector' ? (
            <div className="avatar-selection-screen">
              <div className="selection-header">
                <h1>HoloTutor</h1>
                <p>Learn from History's Greatest Minds</p>
                <div className="feature-badges">
                  <span className="badge"><span className="material-symbols-outlined">school</span>8+ Tutors</span>
                  <span className="badge"><span className="material-symbols-outlined">translate</span>50+ Languages</span>
                  <span className="badge"><span className="material-symbols-outlined">psychology</span>Adaptive Learning</span>
                  <span className="badge"><span className="material-symbols-outlined">mic</span>Voice Interaction</span>
                </div>
                <button
                  className="create-avatar-btn"
                  onClick={() => setShowAvatarCreator(true)}
                >
                  <span className="material-symbols-outlined">add_photo_alternate</span>
                  Create Your Own Tutor
                </button>
              </div>
              <AvatarSelector onSelect={() => setCurrentView('tutoring')} />

              {/* Avatar Creator Modal */}
              <AvatarCreator
                isOpen={showAvatarCreator}
                onClose={() => setShowAvatarCreator(false)}
                onAvatarCreated={handleAvatarCreated}
              />
            </div>
          ) : (
            <TutoringInterface socket={socket} onBack={() => setCurrentView('selector')} />
            )}
          </AvatarContextProvider>
        </LiveAPIProvider>
      </div>
    </ErrorBoundary>
  );
}

export default App;
