"""
Audio Extraction Module

This module handles extracting audio from video files using ffmpeg.
Supports multiple video formats: MP4, AVI, MOV, MKV, etc.
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extracts audio from video files using ffmpeg."""
    
    # Supported video formats
    SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    
    def __init__(self):
        """Initialize the AudioExtractor."""
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is installed and accessible."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logger.info("ffmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg is not installed or not in PATH. "
                "Please install ffmpeg: https://ffmpeg.org/download.html"
            )
    
    def is_supported_format(self, file_path):
        """
        Check if the file format is supported.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            bool: True if format is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def get_video_duration(self, video_path):
        """
        Get the duration of a video file in seconds.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            float: Duration in seconds
            
        Raises:
            RuntimeError: If duration cannot be determined
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            # Use ffprobe to get video duration
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            
            duration = float(result.stdout.strip())
            logger.info(f"Video duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            return duration
            
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.warning(f"Could not determine video duration: {e}")
            return None
    
    def extract_audio(self, video_path, output_path=None, audio_format='wav'):
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the input video file
            output_path: Path for the output audio file (optional)
            audio_format: Output audio format (default: 'wav')
            
        Returns:
            str: Path to the extracted audio file
            
        Raises:
            ValueError: If video format is not supported
            RuntimeError: If extraction fails
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self.is_supported_format(video_path):
            raise ValueError(
                f"Unsupported video format: {video_path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Generate output path if not provided
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(
                temp_dir,
                f"{video_path.stem}_audio.{audio_format}"
            )
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path = str(output_path)
        
        logger.info(f"Extracting audio from {video_path} to {output_path}")
        
        # Use ffmpeg to extract audio
        # -i: input file
        # -vn: disable video
        # -acodec: audio codec (pcm_s16le for WAV)
        # -ar: sample rate (16000 Hz is optimal for Whisper)
        # -ac: audio channels (1 for mono)
        # -y: overwrite output file if exists
        try:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le' if audio_format == 'wav' else 'libmp3lame',
                '-ar', '16000',  # Sample rate (Whisper works best with 16kHz)
                '-ac', '1',  # Mono audio
                '-y',  # Overwrite output
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            if not os.path.exists(output_path):
                raise RuntimeError("Audio extraction completed but output file not found")
            
            logger.info(f"Audio extracted successfully to {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore')
            logger.error(f"ffmpeg error: {error_msg}")
            raise RuntimeError(f"Failed to extract audio: {error_msg}")
    
    def cleanup_temp_file(self, file_path):
        """
        Delete a temporary audio file.
        
        Args:
            file_path: Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")

