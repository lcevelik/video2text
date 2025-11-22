"""
Transcription Module

This module handles audio transcription using OpenAI Whisper.
Supports multiple model sizes and GPU acceleration.
"""

import os
import sys
import re
import logging
import torch
import shutil
import subprocess
import platform
from io import StringIO

import whisper
import threading

logger = logging.getLogger(__name__)

# Global cache for loaded Whisper models to prevent reloading
# Key: model_size (str), Value: whisper.model object
_GLOBAL_MODEL_CACHE = {}
_GLOBAL_CACHE_LOCK = threading.Lock()


class ProgressInterceptor:
    """Intercepts stderr to capture Whisper's tqdm progress and forward to callback."""

    def __init__(self, original_stderr, progress_callback=None, base_percent=50, range_percent=45):
        """
        Args:
            original_stderr: Original stderr stream to forward output to
            progress_callback: Callback function to call with progress updates
            base_percent: Base percentage to start from (default 50)
            range_percent: Range of percentages to cover (default 45, so 50-95)
        """
        self.original_stderr = original_stderr
        self.progress_callback = progress_callback
        self.base_percent = base_percent
        self.range_percent = range_percent
        self.buffer = ""

    def write(self, text):
        """Intercept write calls to stderr."""
        # Forward to original stderr for terminal display
        self.original_stderr.write(text)

        # Parse progress if we have a callback
        if self.progress_callback and text:
            self.buffer += text
            # Look for tqdm progress patterns like "25%", " 50%|", etc.
            # tqdm outputs format: "  5%|▌         | 1/20 [00:01<00:19,  1.03s/it]"
            match = re.search(r'(\d+)%', text)
            if match:
                whisper_percent = int(match.group(1))
                # Map Whisper's 0-100% to our range (e.g., 50-95%)
                overall_percent = self.base_percent + int((whisper_percent / 100.0) * self.range_percent)
                overall_percent = max(0, min(100, overall_percent))
                try:
                    # Try calling with message and percent
                    self.progress_callback(f"Transcribing: {whisper_percent}%", overall_percent)
                except TypeError:
                    # Callback only accepts message
                    try:
                        self.progress_callback(f"Transcribing: {whisper_percent}%")
                    except:
                        pass

    def flush(self):
        """Forward flush calls to original stderr."""
        self.original_stderr.flush()


class Transcriber:
    """Handles audio transcription using OpenAI Whisper."""
    
    # Available Whisper model sizes (including English-only variants where available)
    MODEL_SIZES = [
        'tiny', 'tiny.en',
        'base', 'base.en',
        'small', 'small.en',
        'medium', 'medium.en',
        'large'
    ]
    
    # Transcription speed factors (seconds of audio per second of processing)
    # Updated based on actual performance data from RTX 4080 GPU
    # Real-time factors (multiplier - how many times faster than real-time)
    # e.g., 11.0 means transcription is 11x faster than real-time (1 minute video = ~5.5 seconds)
    SPEED_FACTORS = {
        'tiny': {'cpu': 10.0, 'cuda': 100.0},      # CPU: 10x real-time, GPU: 100x real-time
        'base': {'cpu': 6.7, 'cuda': 67.0},       # CPU: ~6.7x real-time, GPU: ~67x real-time
        'small': {'cpu': 3.3, 'cuda': 33.0},      # CPU: ~3.3x real-time, GPU: ~33x real-time
        'medium': {'cpu': 1.7, 'cuda': 11.0},     # CPU: ~1.7x real-time, GPU: ~11x real-time
        'large': {'cpu': 0.8, 'cuda': 5.5}        # CPU: ~0.8x real-time, GPU: ~5.5x real-time
    }
    
    # Model loading time estimates (seconds)
    MODEL_LOAD_TIMES = {
        'tiny': {'cpu': 2, 'cuda': 3},
        'base': {'cpu': 3, 'cuda': 4},
        'small': {'cpu': 5, 'cuda': 6},
        'medium': {'cpu': 8, 'cuda': 10},
        'large': {'cpu': 15, 'cuda': 20}
    }
    
    def __init__(self, model_size='base'):
        """
        Initialize the Transcriber.

        Args:
            model_size: Size of the Whisper model to use
        """
        self.model_size = model_size
        self.model = None
        self.device = self._get_device()
        logger.info(f"Initialized Transcriber with model '{model_size}' using OpenAI Whisper on device '{self.device}'")
    
    def _get_device(self):
        """
        Determine the best available device (CUDA GPU, Apple Silicon MPS, or CPU).

        Returns:
            str: Device name ('cuda', 'mps', or 'cpu')
        """
        # Allow override: FONIXFLOW_DEVICE=cpu|cuda|mps
        forced = os.environ.get('FONIXFLOW_DEVICE', '').strip().lower()
        if forced in ('cpu', 'cuda', 'mps'):
            if forced == 'cuda' and not torch.cuda.is_available():
                logger.warning("FONIXFLOW_DEVICE=cuda set, but torch.cuda.is_available() is False")
            elif forced == 'mps' and not torch.backends.mps.is_available():
                logger.warning("FONIXFLOW_DEVICE=mps set, but torch.backends.mps.is_available() is False")
            else:
                if forced == 'cuda':
                    try:
                        logger.info(f"✓ Using NVIDIA GPU (forced): {torch.cuda.get_device_name(0)}")
                    except Exception:
                        logger.info("✓ Using NVIDIA GPU (forced)")
                elif forced == 'mps':
                    logger.info("✓ Using Apple Silicon GPU (MPS) (forced)")
                else:
                    logger.info("Using CPU (forced)")
                return forced

        if torch.cuda.is_available():
            device = 'cuda'
            try:
                name = torch.cuda.get_device_name(0)
            except Exception:
                name = 'NVIDIA GPU'
            logger.info(f"✓ Using NVIDIA GPU: {name} (CUDA {torch.version.cuda or 'unknown'})")
        elif torch.backends.mps.is_available():
            device = 'mps'
            logger.info("✓ Using Apple Silicon GPU (Metal Performance Shaders) - Optimized for M1/M2/M3/M4!")
            logger.info("Note: Using full precision (FP32) on MPS for numerical stability with large models")
        else:
            device = 'cpu'
            # Provide helpful diagnostics for Windows/NVIDIA
            if platform.system() == 'Windows':
                has_nvidia = False
                try:
                    if shutil.which('nvidia-smi'):
                        proc = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True, timeout=2)
                        has_nvidia = (proc.returncode == 0 and proc.stdout.strip() != '')
                except Exception:
                    pass
                cuda_built = bool(getattr(torch.version, 'cuda', None))
                if has_nvidia and not torch.cuda.is_available():
                    if not cuda_built:
                        logger.info("Using CPU (PyTorch installed without CUDA support)")
                        logger.info("→ NVIDIA GPU detected but current torch wheel is CPU-only.")
                        logger.info("→ To enable GPU, install CUDA-enabled PyTorch, e.g.:")
                        logger.info("   pip uninstall -y torch torchaudio torchvision")
                        logger.info("   pip install --index-url https://download.pytorch.org/whl/cu121 torch torchaudio torchvision")
                    else:
                        logger.info("Using CPU (torch CUDA build present but driver/runtime unavailable)")
                        logger.info("→ Ensure NVIDIA driver and CUDA runtime match the torch build.")
                else:
                    logger.info("Using CPU (no GPU acceleration available)")
            else:
                logger.info("Using CPU (no GPU acceleration available)")
        return device
    
    def load_model(self, progress_callback=None):
        """
        Load the Whisper model.

        Args:
            progress_callback: Optional callback function for progress updates

        Returns:
            Loaded Whisper model
        """
        if self.model is not None:
            return self.model

        if progress_callback:
            progress_callback("Loading Whisper model...")

        logger.info(f"Loading Whisper model: {self.model_size}")

        try:
            # Check global cache first
            with _GLOBAL_CACHE_LOCK:
                if self.model_size in _GLOBAL_MODEL_CACHE:
                    logger.info(f"Reusing cached Whisper model: {self.model_size}")
                    self.model = _GLOBAL_MODEL_CACHE[self.model_size]
                    logger.info(f"OpenAI Whisper model '{self.model_size}' loaded successfully (from cache)")
                    if progress_callback:
                        progress_callback("Model loaded successfully")
                    return self.model

            # Not in cache, load it
            logger.info(f"Loading new Whisper model into memory: {self.model_size}")
            model = whisper.load_model(
                self.model_size,
                device=self.device,
                download_root=os.path.join(os.path.expanduser("~"), ".cache", "whisper")
            )
            
            # Store in cache
            with _GLOBAL_CACHE_LOCK:
                _GLOBAL_MODEL_CACHE[self.model_size] = model
                self.model = model
                
            logger.info(f"OpenAI Whisper model '{self.model_size}' loaded successfully")

            if progress_callback:
                progress_callback("Model loaded successfully")

            return self.model

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe(self, audio_path, language=None, initial_prompt=None, progress_callback=None, word_timestamps=False):
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr'). If None, auto-detect.
            initial_prompt: Optional initial prompt/instructions to guide transcription.
                           Useful for speaker recognition, context, or specific terminology.
            progress_callback: Optional callback function for progress updates (can accept percent as second arg)
            word_timestamps: If True, include word-level timestamps in segments
            
        Returns:
            dict: Transcription result with keys: 'text', 'segments', 'language'
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if self.model is None:
            self.load_model(progress_callback)
        
        if progress_callback:
            # Call with just message (callback may or may not accept percent)
            try:
                progress_callback("Starting transcription...")
            except TypeError:
                # Callback doesn't accept arguments, skip
                pass

        logger.info(f"Transcribing audio: {audio_path}")
        if initial_prompt:
            logger.info(f"Using initial prompt: {initial_prompt[:100]}...")

        # Set up progress interception if callback provided
        original_stderr = sys.stderr
        try:
            # Use standard OpenAI Whisper
            transcribe_kwargs = {
                'language': language,
                'verbose': True if progress_callback else False,
                # Only enable FP16 for CUDA (MPS has numerical stability issues with FP16)
                'fp16': (self.device == 'cuda')
            }

            if word_timestamps:
                transcribe_kwargs['word_timestamps'] = True

            if initial_prompt:
                transcribe_kwargs['initial_prompt'] = initial_prompt

            # For MPS device, pre-load audio as float32 to avoid float64 conversion errors
            audio_input = audio_path
            if self.device == 'mps':
                try:
                    import librosa
                    import numpy as np
                    logger.info("Pre-loading audio as float32 for MPS compatibility...")
                    # Load audio at 16kHz (Whisper's expected sample rate) as float32
                    audio_data, sr = librosa.load(audio_path, sr=16000, mono=True, dtype=np.float32)
                    audio_input = audio_data
                    logger.info(f"Audio loaded: {len(audio_data)} samples at {sr}Hz (float32)")
                except ImportError:
                    logger.warning("librosa not available, passing file path to Whisper (may cause MPS dtype issues)")
                except Exception as e:
                    logger.warning(f"Failed to pre-load audio: {e}, passing file path to Whisper")

            # Intercept stderr to capture tqdm progress if callback provided
            if progress_callback:
                sys.stderr = ProgressInterceptor(original_stderr, progress_callback, base_percent=50, range_percent=45)

            result = self.model.transcribe(audio_input, **transcribe_kwargs)

            # Restore stderr
            if progress_callback:
                sys.stderr = original_stderr

            logger.info("Transcription completed successfully")

            if progress_callback:
                try:
                    progress_callback("Transcription completed", 95)
                except TypeError:
                    try:
                        progress_callback("Transcription completed")
                    except:
                        pass

            logger.info("Transcription completed successfully")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            if sys.stderr != original_stderr:
                sys.stderr = original_stderr
            raise RuntimeError(f"Transcription failed: {e}")
    
    def format_as_srt(self, transcription_result):
        """
        Format transcription result as SRT subtitle file.
        
        Args:
            transcription_result: Result dictionary from transcribe()
            
        Returns:
            str: SRT formatted subtitle content
        """
        segments = transcription_result.get('segments', [])
        srt_content = []
        
        for i, segment in enumerate(segments, start=1):
            start_time = self._format_timestamp(segment['start'])
            end_time = self._format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            srt_content.append(f"{i}\n{start_time} --> {end_time}\n{text}\n")
        
        return "\n".join(srt_content)
    
    def _format_timestamp(self, seconds):
        """
        Format seconds as SRT timestamp (HH:MM:SS,mmm).
        
        Args:
            seconds: Time in seconds
            
        Returns:
            str: Formatted timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_model_info(self):
        """
        Get information about the current model.
        
        Returns:
            dict: Model information
        """
        return {
            'model_size': self.model_size,
            'device': self.device,
            'is_loaded': self.model is not None,
            'cuda_available': torch.cuda.is_available()
        }
    
    @staticmethod
    def estimate_transcription_time(video_duration_seconds, model_size, device='cpu', model_already_loaded=False):
        """
        Estimate transcription time based on video duration, model size, and device.
        
        Args:
            video_duration_seconds: Duration of video/audio in seconds
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            device: 'cpu' or 'cuda'
            model_already_loaded: Whether model is already loaded in memory
            
        Returns:
            dict: Estimation with keys: 'total_seconds', 'transcription_seconds', 
                  'loading_seconds', 'extraction_seconds', 'formatted_time'
        """
        if video_duration_seconds is None or video_duration_seconds <= 0:
            return {
                'total_seconds': None,
                'transcription_seconds': None,
                'loading_seconds': 0,
                'extraction_seconds': 10,  # Default estimate for audio extraction
                'formatted_time': 'Unknown'
            }
        
        # Get real-time factor for the model and device (how many times faster than real-time)
        base_name = model_size.replace('.en', '') if isinstance(model_size, str) else model_size
        realtime_factor = Transcriber.SPEED_FACTORS.get(base_name, {}).get(device, 10.0)
        
        # Estimate transcription time (video duration / real-time factor)
        # e.g., 1963 seconds video with 11x factor = 1963/11 = 178 seconds
        transcription_seconds = video_duration_seconds / realtime_factor if realtime_factor > 0 else video_duration_seconds
        
        # Model loading time (only if not already loaded)
        loading_seconds = 0
        if not model_already_loaded:
            loading_seconds = Transcriber.MODEL_LOAD_TIMES.get(base_name, {}).get(device, 5)
        
        # Audio extraction time (rough estimate: ~5-15 seconds depending on video length)
        extraction_seconds = min(15, max(5, video_duration_seconds * 0.01))
        
        # Total time
        total_seconds = extraction_seconds + loading_seconds + transcription_seconds
        
        # Format time
        formatted_time = Transcriber._format_estimated_time(total_seconds)
        
        return {
            'total_seconds': total_seconds,
            'transcription_seconds': transcription_seconds,
            'loading_seconds': loading_seconds,
            'extraction_seconds': extraction_seconds,
            'formatted_time': formatted_time
        }
    
    @staticmethod
    def _format_estimated_time(seconds):
        """
        Format estimated time in a human-readable format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            str: Formatted time string
        """
        if seconds is None:
            return "Unknown"
        
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if secs > 0:
                return f"{minutes}m {secs}s"
            return f"{minutes} minutes"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours} hour{'s' if hours > 1 else ''}"
    
    @staticmethod
    def get_model_description(model_size):
        """
        Get a detailed description of a model.
        
        Args:
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large')
            
        Returns:
            dict: Model description with keys: 'description', 'speed', 'accuracy', 'use_case'
        """
        descriptions = {
            'tiny': {
                'description': 'Fastest model, smallest size',
                'speed': 'Very Fast (10x real-time on CPU, 100x on GPU)',
                'accuracy': 'Basic - Good for simple, clear speech',
                'use_case': 'Quick tests, low accuracy needs, very short videos',
                'size': '~39 MB'
            },
            'base': {
                'description': 'Balanced speed and accuracy (Recommended)',
                'speed': 'Fast (~6.7x real-time on CPU, ~67x on GPU)',
                'accuracy': 'Good - Handles most common scenarios well',
                'use_case': 'Most users, general transcription, balanced needs',
                'size': '~74 MB'
            },
            'small': {
                'description': 'Better accuracy, moderate speed',
                'speed': 'Medium (~3.3x real-time on CPU, ~33x on GPU)',
                'accuracy': 'Better - Improved handling of accents and noise',
                'use_case': 'Better accuracy needed, can wait a bit longer',
                'size': '~244 MB'
            },
            'medium': {
                'description': 'High accuracy, slower processing',
                'speed': 'Slow (~1.7x real-time on CPU, ~17x on GPU)',
                'accuracy': 'High - Excellent for complex audio',
                'use_case': 'High accuracy critical, complex audio, multiple speakers',
                'size': '~769 MB'
            },
            'large': {
                'description': 'Best accuracy, very slow processing',
                'speed': 'Very Slow (~0.8x real-time on CPU, ~8x on GPU)',
                'accuracy': 'Best - Maximum quality transcription',
                'use_case': 'Maximum accuracy, professional use, very complex audio',
                'size': '~3 GB'
            }
        }
        
        # If an English-only variant is requested, map to the base model's description
        # and annotate that it is English-only optimized.
        if isinstance(model_size, str) and model_size.endswith('.en'):
            base = model_size[:-3]
            base_desc = descriptions.get(base, descriptions['base']).copy()
            base_desc['description'] = base_desc['description'] + ' (English-only optimized)'
            return base_desc

        return descriptions.get(model_size, descriptions['base'])

