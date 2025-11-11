"""
Audio Extraction Module

This module handles extracting audio from video files and preparing audio files for transcription.
Supports multiple video formats: MP4, AVI, MOV, MKV, etc.
Also supports direct audio file formats: MP3, WAV, M4A, FLAC, OGG, etc.
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extracts audio from video files or prepares audio files for transcription using ffmpeg."""
    
    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    
    # Supported audio formats (Whisper can handle these directly, but we may need to convert for optimal format)
    SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.opus', '.mp2'}
    
    # All supported formats
    SUPPORTED_FORMATS = SUPPORTED_VIDEO_FORMATS | SUPPORTED_AUDIO_FORMATS
    
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
            file_path: Path to the media file (video or audio)
            
        Returns:
            bool: True if format is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def is_audio_file(self, file_path):
        """
        Check if the file is an audio file (not a video file).
        
        Args:
            file_path: Path to the media file
            
        Returns:
            bool: True if file is an audio file
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_AUDIO_FORMATS
    
    def is_video_file(self, file_path):
        """
        Check if the file is a video file.
        
        Args:
            file_path: Path to the media file
            
        Returns:
            bool: True if file is a video file
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_VIDEO_FORMATS
    
    def get_media_duration(self, media_path):
        """
        Get the duration of a media file (video or audio) in seconds.
        
        Args:
            media_path: Path to the media file (video or audio)
            
        Returns:
            float: Duration in seconds, or None if cannot be determined
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        media_path = Path(media_path)
        
        if not media_path.exists():
            raise FileNotFoundError(f"Media file not found: {media_path}")
        
        try:
            # Use ffprobe to get media duration (works for both video and audio)
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(media_path)
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            
            duration = float(result.stdout.strip())
            file_type = "audio" if self.is_audio_file(media_path) else "video"
            logger.info(f"{file_type.capitalize()} duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            return duration
            
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.warning(f"Could not determine media duration: {e}")
            return None
    
    def get_video_duration(self, video_path):
        """
        Get the duration of a video file in seconds (backward compatibility).
        
        Args:
            video_path: Path to the video file
            
        Returns:
            float: Duration in seconds, or None if cannot be determined
        """
        return self.get_media_duration(video_path)
    
    def extract_audio(self, media_path, output_path=None, audio_format='wav'):
        """
        Extract or prepare audio from a media file (video or audio).
        - If input is a video file: extracts audio from video
        - If input is an audio file: converts to optimal format for Whisper (16kHz mono WAV)
        
        Args:
            media_path: Path to the input media file (video or audio)
            output_path: Path for the output audio file (optional)
            audio_format: Output audio format (default: 'wav')
            
        Returns:
            str: Path to the prepared audio file (may be original if already optimal format)
            
        Raises:
            ValueError: If media format is not supported
            RuntimeError: If extraction/conversion fails
        """
        media_path = Path(media_path)
        
        if not media_path.exists():
            raise FileNotFoundError(f"Media file not found: {media_path}")
        
        if not self.is_supported_format(media_path):
            raise ValueError(
                f"Unsupported media format: {media_path.suffix}. "
                f"Supported video formats: {', '.join(sorted(self.SUPPORTED_VIDEO_FORMATS))}. "
                f"Supported audio formats: {', '.join(sorted(self.SUPPORTED_AUDIO_FORMATS))}"
            )
        
        # If it's already a WAV file, check if we can use it directly
        # For now, we'll always convert to ensure optimal format (16kHz mono)
        # This ensures consistency and optimal Whisper performance
        
        # Generate output path if not provided
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(
                temp_dir,
                f"{media_path.stem}_audio.{audio_format}"
            )
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path = str(output_path)
        
        if self.is_audio_file(media_path):
            logger.info(f"Converting audio file {media_path} to optimal format for Whisper")
        else:
            logger.info(f"Extracting audio from video {media_path} to {output_path}")
        
        # Use ffmpeg to extract/convert audio
        # -i: input file
        # -vn: disable video (for video files)
        # -acodec: audio codec (pcm_s16le for WAV)
        # -ar: sample rate (16000 Hz is optimal for Whisper)
        # -ac: audio channels (1 for mono)
        # -y: overwrite output file if exists
        try:
            cmd = ['ffmpeg', '-i', str(media_path)]
            
            # Only add -vn for video files
            if self.is_video_file(media_path):
                cmd.append('-vn')  # No video
            
            # Add audio processing options
            cmd.extend([
                '-acodec', 'pcm_s16le' if audio_format == 'wav' else 'libmp3lame',
                '-ar', '16000',  # Sample rate (Whisper works best with 16kHz)
                '-ac', '1',  # Mono audio
                '-y',  # Overwrite output
                output_path
            ])
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            if not os.path.exists(output_path):
                raise RuntimeError("Audio processing completed but output file not found")
            
            action = "converted" if self.is_audio_file(media_path) else "extracted"
            logger.info(f"Audio {action} successfully to {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore')
            logger.error(f"ffmpeg error: {error_msg}")
            action = "convert" if self.is_audio_file(media_path) else "extract"
            raise RuntimeError(f"Failed to {action} audio: {error_msg}")
    
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

