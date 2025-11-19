# AI Tutor Prototype: Frontend and MediaMixer

This document outlines the architecture and functionality of the AI Tutor prototype, focusing on the interaction between the React-based frontend (`live-api-web-console`) and the Python-based `MediaMixer`.

## Overview

The system is designed to create a rich, multi-stream video feed for an AI tutor powered by Gemini. It combines a live scratchpad, a screen share, and a camera feed into a single video stream, which is then sent to the Gemini API for analysis.

## Components

### 1. MediaMixer (`/MediaMixer/media_mixer.py`)

The `MediaMixer` is a Python server that uses `websockets` and `OpenCV` to perform the following tasks:

- **Receives Video Feeds:** It accepts a live "scratchpad" feed from the frontend via a WebSocket connection.
- **Captures Local Feeds:** It captures the local webcam and screen share using `cv2.VideoCapture` and `mss`.
- **Mixes Video Streams:** It combines the three video sources (scratchpad, screen share, camera) into a single, vertically-stacked video frame.
- **Broadcasts Mixed Stream:** It encodes the mixed frame as a base64 JPEG and broadcasts it to all connected WebSocket clients.

### 2. Frontend (`/live-api-web-console`)

The frontend is a React application that serves as the user interface and the control center for the system.

- **Main UI:** The left side of the UI contains the "scratchpad" area, which includes the `Altair` component, a text area, and a local video preview.
- **Scratchpad Capture:** The `<ScratchpadCapture>` component uses the `html2canvas` library to take screenshots of the main UI area at approximately 15 frames per second. These screenshots are sent to the `MediaMixer` via a WebSocket to be used as the scratchpad feed.
- **MediaMixer Display:** The `<MediaMixerDisplay>` component on the right side of the UI receives the mixed video stream from the `MediaMixer` and displays it to the user.
- **Control Tray:** The `<ControlTray>` component contains buttons to toggle the camera and screen share feeds on the `MediaMixer`. It also manages the connection to the Gemini API.
- **Gemini Integration:** When the user clicks the "play" button, the system begins sending the mixed video stream (captured from the `MediaMixerDisplay`) to the Gemini API for processing.

## Communication Flow

1.  **Initialization:** The React frontend establishes a single, persistent WebSocket connection to the `MediaMixer` server.
2.  **Scratchpad to Mixer:** The frontend continuously sends screenshots of the main UI to the `MediaMixer`.
3.  **Mixer to Frontend:** The `MediaMixer` combines the scratchpad, camera, and screen share, and broadcasts the final mixed video back to the frontend.
4.  **Frontend to Gemini:** When connected, the frontend takes the mixed video stream, encodes it, and sends it to the Gemini API.
5.  **Control Commands:** The frontend sends commands (e.g., `start_camera`, `stop_screen`) to the `MediaMixer` over the same WebSocket to toggle the video feeds.

## How to Run

1.  **Start the MediaMixer:**
    ```bash
    python /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor/prototypes/tutorinteractions/MediaMixer/media_mixer.py
    ```

2.  **Start the Frontend:**
    ```bash
    cd /Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor/prototypes/tutorinteractions/live-api-web-console
    npm start
    ```
