# Mobile Version Strategy

To run FonixFlow on mobile, we cannot simply "compile" the Python code to an APK/IPA because the dependencies (PyTorch, OpenAI Whisper, FFmpeg) are too heavy and architecturally different for mobile processors (ARM) in a standard Python environment.

## The Solution: Client-Server Architecture

We will utilize the **Web Version** you just created.

1.  **The Server (Your PC):** Runs the heavy lifting (Python/FastAPI + Whisper Models + GPU).
2.  **The Client (Your Phone):** Runs the lightweight interface (React) in the mobile browser.

This gives you the full power of the Desktop `large` models on your phone without draining its battery or storage.

## Features Implemented
I have updated the Web Frontend to be **fully responsive (Mobile-First)**:
*   **Collapsible Sidebar:** Hidden on mobile, accessible via Hamburger menu.
*   **Touch-Friendly:** Larger tap targets for upload and controls.
*   **Responsive Layout:** Adjusts to phone screens automatically.

## How to Use on Mobile

1.  **Start the Backend (PC):**
    ```bash
    # Find your PC's local IP address (e.g., 192.168.1.15)
    # Run the server on 0.0.0.0 to allow external access
    uvicorn web.backend.main:app --host 0.0.0.0 --port 8000
    ```

2.  **Start the Frontend (PC):**
    ```bash
    cd web/frontend
    npm run dev -- --host
    ```
    *The `--host` flag exposes it to your network.*

3.  **Access on Phone:**
    *   Open Chrome/Safari on your phone.
    *   Go to `http://<YOUR_PC_IP>:5173` (e.g., `http://192.168.1.15:5173`).
    *   You can now upload files from your phone's gallery or file system!

## Native Mobile App (Future Path)
If you truly need a standalone offline mobile app, you would need to rewrite the backend using:
*   **CoreML (iOS)** or **TFLite (Android)** ports of Whisper.
*   **React Native** or **Flutter** for the UI.
*   **whisper.cpp** for inference.
*   *Note: This would be a completely separate project from the Python codebase.*
