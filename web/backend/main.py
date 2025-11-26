import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add project root to sys.path to allow importing app and transcription modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.transcriber import Transcriber
from app.audio_extractor import AudioExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fonixflow-web")

app = FastAPI(title="FonixFlow Web API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Transcriber instance (lazy loaded)
transcriber_instance = None

def get_transcriber(model_size: str = "base"):
    global transcriber_instance
    # Reload if model size changes (simple implementation)
    if transcriber_instance is None or transcriber_instance.model_size != model_size:
        logger.info(f"Loading Transcriber with model: {model_size}")
        transcriber_instance = Transcriber(model_size=model_size)
    return transcriber_instance

class TranscriptionResponse(BaseModel):
    text: str
    language: str
    segments: List[dict]
    duration: float

@app.get("/")
def read_root():
    return {"status": "online", "app": "FonixFlow Web"}

@app.get("/models")
def get_available_models():
    """Return available Whisper models and their descriptions."""
    return Transcriber.get_model_description("base") # Just return base desc structure or list all

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    model_size: str = Form("base"),
    language: Optional[str] = Form(None)
):
    """
    Handle audio/video upload and transcription.
    """
    logger.info(f"Received transcription request: {file.filename} (Model: {model_size})")
    
    # Create temp file
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    temp_file_path = temp_dir / file.filename
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Check if conversion is needed using AudioExtractor
        extractor = AudioExtractor()
        audio_path = temp_file_path
        
        if extractor.is_video_file(temp_file_path) or not extractor.is_audio_file(temp_file_path):
            logger.info("Extracting audio from video...")
            # Ensure ffmpeg is configured
            AudioExtractor.configure_ffmpeg_converter()
            audio_path = extractor.extract_audio(temp_file_path)
            
        # Transcribe
        transcriber = get_transcriber(model_size)
        
        # Define a progress callback (just logs for now, could be websocket)
        def progress_cb(msg, pct=None):
            logger.info(f"Progress: {msg} ({pct}%)")

        result = transcriber.transcribe(
            str(audio_path),
            language=language,
            progress_callback=progress_cb
        )
        
        # Cleanup temp audio if it was extracted
        if audio_path != temp_file_path:
            os.remove(audio_path)
            
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"]
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup uploaded file
        if temp_file_path.exists():
            os.remove(temp_file_path)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
