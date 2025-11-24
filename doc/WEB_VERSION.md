# Web Version Architecture Analysis

## Overview
Porting FonixFlow to a web application involves moving the transcription and audio processing logic to a Python backend (FastAPI) and rebuilding the UI in a modern web framework (React).

## Architecture

### Backend (FastAPI)
*   **API Endpoints:**
    *   `POST /transcribe`: Accepts audio file upload, runs Whisper, returns JSON/SRT.
    *   `GET /status/{task_id}`: Returns progress of long-running transcription.
    *   `WS /ws/audio`: WebSocket for real-time audio streaming (recording).
*   **Workers:**
    *   Use `Celery` or `FastAPI BackgroundTasks` to handle Whisper processing off the main thread.
*   **Reused Code:**
    *   `app/transcriber.py`: Can be used almost "as-is" (with some minor adjustments for logging/progress callbacks).
    *   `transcription/`: Core logic (segmentation, language detection) is fully reusable.

### Frontend (React + Tailwind)
*   **UI Components:**
    *   Recreate the Sidebar/Tabs layout using React components.
    *   Use `lucide-react` for icons.
    *   Use `shadcn/ui` for polished look matching the current Qt theme.
*   **Audio Recording:**
    *   Use MediaRecorder API in browser to capture microphone.
    *   **Challenge:** System audio capture is restricted in browsers. You cannot easily record "Speaker" audio (loopback) from a web page unless the user shares their screen/tab with audio.
    *   **Solution:** Use "Screen Share -> Share Audio" feature in browser `getDisplayMedia` API.

### Challenges & Solutions

1.  **System Audio (Loopback) Recording:**
    *   *Qt App:* Uses `sounddevice`/`WASAPI`/`ScreenCaptureKit` for native low-level access.
    *   *Web App:* Must use `navigator.mediaDevices.getDisplayMedia({ audio: true, video: true })`. User must select the screen/tab to share. This is less seamless than the desktop app.

2.  **Real-time VU Meter:**
    *   *Qt App:* Reads raw audio chunks from thread.
    *   *Web App:* Use Web Audio API (`AnalyserNode`) on the client side to visualize the microphone stream before sending it to the server.

3.  **Offline Capability:**
    *   The current desktop app runs locally/offline.
    *   A web version running on `localhost` (via Docker or simple installer) retains this benefit.
    *   A hosted web version would require uploading large audio files to a server, raising privacy/bandwidth costs.

## Recommended Stack
*   **Backend:** Python 3.11, FastAPI, Uvicorn.
*   **Frontend:** React, Vite, Tailwind CSS.
*   **Packaging:** Docker Compose (for easy local deployment).

## Roadmap
1.  **Backend Prototype:** Create `server.py` with FastAPI wrapping `Transcriber`.
2.  **Frontend Shell:** Create React app with file upload.
3.  **Integration:** Connect upload -> transcribe API.
4.  **Recording:** Implement browser-based recorder.
