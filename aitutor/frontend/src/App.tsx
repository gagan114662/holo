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
import { AvatarContextProvider } from "./contexts/AvatarContext";
import SidePanel from "./components/side-panel/SidePanel";
import MediaMixerDisplay from "./components/media-mixer-display/MediaMixerDisplay";
import ScratchpadCapture from "./components/scratchpad-capture/ScratchpadCapture";
import QuestionDisplay from "./components/question-display/QuestionDisplay";
import ControlTray from "./components/control-tray/ControlTray";
import { TalkingAvatar, AvatarSelector } from "./components/avatar";
import AvatarSpeechHandler from "./components/avatar/AvatarSpeechHandler";
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

function App() {
  // this video reference is used for displaying the active stream, whether that is the webcam or screen capture
  const videoRef = useRef<HTMLVideoElement>(null);
  const renderCanvasRef = useRef<HTMLCanvasElement>(null);
  // either the screen capture, the video or null, if null we hide it
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [mixerStream, setMixerStream] = useState<MediaStream | null>(null);
  const mixerVideoRef = useRef<HTMLVideoElement>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isScratchpadOpen, setScratchpadOpen] = useState(false);
  const [currentView, setCurrentView] = useState<AppView>('selector');
  const [isAvatarMinimized, setAvatarMinimized] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    if (mixerVideoRef.current && mixerStream) {
      mixerVideoRef.current.srcObject = mixerStream;
    }
  }, [mixerStream]);

  const handleAvatarSelected = () => {
    setCurrentView('tutoring');
  };

  const handleBackToSelector = () => {
    setCurrentView('selector');
  };

  return (
    <div className="App">
      <LiveAPIProvider options={apiOptions}>
        <AvatarContextProvider>
          {/* Avatar Speech Handler - connects Gemini to Avatar */}
          <AvatarSpeechHandler />

          {currentView === 'selector' ? (
            // Avatar Selection Screen
            <div className="avatar-selection-screen">
              <AvatarSelector onSelect={handleAvatarSelected} />
            </div>
          ) : (
            // Main Tutoring Interface
            <div className="streaming-console">
              <SidePanel />
              <main>
                {/* Top bar with avatar toggle and back button */}
                <div className="top-bar">
                  <button
                    className="back-button"
                    onClick={handleBackToSelector}
                  >
                    <span className="material-symbols-outlined">arrow_back</span>
                    Change Tutor
                  </button>
                  <button
                    className={cn("avatar-toggle", { minimized: isAvatarMinimized })}
                    onClick={() => setAvatarMinimized(!isAvatarMinimized)}
                  >
                    <span className="material-symbols-outlined">
                      {isAvatarMinimized ? "open_in_full" : "close_fullscreen"}
                    </span>
                  </button>
                </div>

                <div className="main-app-area">
                  {/* Avatar Display */}
                  <div className={cn("avatar-panel", { minimized: isAvatarMinimized })}>
                    <TalkingAvatar
                      size={isAvatarMinimized ? "small" : "large"}
                      showName={!isAvatarMinimized}
                    />
                  </div>

                  {/* Question and Scratchpad Area */}
                  <div className="question-panel">
                    <ScratchpadCapture socket={socket}>
                      <QuestionDisplay />
                      {isScratchpadOpen && (
                        <div className="scratchpad-container">
                          <Scratchpad />
                        </div>
                      )}
                    </ScratchpadCapture>
                  </div>

                  {/* Media Mixer (webcam preview etc) */}
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
              </main>
            </div>
          )}
        </AvatarContextProvider>
      </LiveAPIProvider>
    </div>
  );
}

export default App;
