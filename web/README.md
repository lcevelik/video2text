# FonixFlow Web

This is the web-based version of FonixFlow, featuring a FastAPI backend and a React frontend.

## Prerequisites

*   Python 3.10+
*   Node.js 18+
*   FFmpeg (installed on system or configured via environment)

## Quick Start

### 1. Backend (API)

Navigate to the root directory:

```bash
# Create/Activate venv if needed
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r web/backend/requirements.txt
pip install -r requirements.txt

# Run Server
python web/backend/main.py
```

The API will be available at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`.

### 2. Frontend (UI)

Open a new terminal:

```bash
cd web/frontend

# Install dependencies
npm install

# Start Dev Server
npm run dev
```

The UI will be available at `http://localhost:5173`.

## Architecture

*   **Backend:** FastAPI wrapper around the core `app.transcriber.Transcriber` class. Reuses the same Whisper logic as the desktop app.
*   **Frontend:** React (Vite) with Tailwind CSS. Mimics the "Dark Mode" aesthetic of the Qt app.
*   **Storage:** Uploads are temporarily stored in `temp_uploads/` and cleaned up after processing.
