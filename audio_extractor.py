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
        self.ffmpeg_path = self._get_ffmpeg_path()
        self._check_ffmpeg()

    def _get_ffmpeg_path(self):
        import sys
        import os
        exe_dir = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(exe_dir, 'ffmpeg.exe')
        logger.debug(f"Checking for ffmpeg.exe in executable directory: {exe_dir}")
        if os.path.exists(ffmpeg_path):
            logger.debug(f"Found ffmpeg.exe at: {ffmpeg_path}")
            return ffmpeg_path
        logger.debug("ffmpeg.exe not found in executable directory, falling back to PATH")
        return 'ffmpeg'  # Fallback to PATH if not found
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is installed and accessible."""
        try:
            logger.info(f"Trying to run ffmpeg at path: {self.ffmpeg_path}")
            logger.debug(f"Running command: {[self.ffmpeg_path, '-version']}")
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logger.info(f"ffmpeg is available at {self.ffmpeg_path}")
            logger.debug(f"ffmpeg stdout: {result.stdout.decode('utf-8', errors='ignore')}")
            logger.debug(f"ffmpeg stderr: {result.stderr.decode('utf-8', errors='ignore')}")
        except PermissionError as e:
            logger.error(f"PermissionError when running ffmpeg: {e}")
            logger.error(f"ffmpeg path: {self.ffmpeg_path}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Executable directory: {os.path.dirname(os.path.abspath(__file__))}")
            raise RuntimeError(
                f"PermissionError: ffmpeg is not accessible at {self.ffmpeg_path}. "
                "Check file permissions and antivirus settings."
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Error when running ffmpeg: {e}")
            logger.error(f"ffmpeg path: {self.ffmpeg_path}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Executable directory: {os.path.dirname(os.path.abspath(__file__))}")
            raise RuntimeError(
                f"ffmpeg is not installed or not accessible at {self.ffmpeg_path}. "
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
            logger.error(f"Media file not found: {media_path}")
            raise FileNotFoundError(f"Media file not found: {media_path}")
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(media_path)
            ]
            logger.debug(f"Running ffprobe command: {cmd}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            logger.debug(f"ffprobe stdout: {result.stdout}")
            logger.debug(f"ffprobe stderr: {result.stderr}")
            duration = float(result.stdout.strip())
            file_type = "audio" if self.is_audio_file(media_path) else "video"
            logger.info(f"{file_type.capitalize()} duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            return duration
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.warning(f"Could not determine media duration: {e}")
            logger.debug(f"ffprobe command failed or output invalid for file: {media_path}")
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
    
    def extract_audio(self, media_path, output_path=None, audio_format='wav', progress_callback=None):
        """
        Extract or prepare audio from a media file (video or audio).
        - If input is a video file: extracts audio from video
        - If input is an audio file: converts to optimal format for Whisper (16kHz mono WAV)

        OPTIMIZED: Now supports progress callbacks for better UX.

        Args:
            media_path: Path to the input media file (video or audio)
            output_path: Path for the output audio file (optional)
            audio_format: Output audio format (default: 'wav')
            progress_callback: Optional callback function(message, percentage) for progress updates

        Returns:
            str: Path to the prepared audio file (may be original if already optimal format)

        Raises:
            ValueError: If media format is not supported
            RuntimeError: If extraction/conversion fails
        """
        media_path = Path(media_path)
        if not media_path.exists():
            logger.error(f"Media file not found: {media_path}")
            raise FileNotFoundError(f"Media file not found: {media_path}")
        if not self.is_supported_format(media_path):
            logger.error(f"Unsupported media format: {media_path.suffix}")
            logger.error(f"Supported video formats: {', '.join(sorted(self.SUPPORTED_VIDEO_FORMATS))}")
            logger.error(f"Supported audio formats: {', '.join(sorted(self.SUPPORTED_AUDIO_FORMATS))}")
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
        logger.debug(f"Output audio path: {output_path}")
        if self.is_audio_file(media_path):
            logger.info(f"Converting audio file {media_path} to optimal format for Whisper")
            action_present = "Converting"
            action_past = "converted"
        else:
            logger.info(f"Extracting audio from video {media_path} to {output_path}")
            action_present = "Extracting"
            action_past = "extracted"
        if progress_callback:
            progress_callback(f"{action_present} audio...", 5)
        # Use ffmpeg to extract/convert audio
        # -i: input file
        # -vn: disable video (for video files)
        # -acodec: audio codec (pcm_s16le for WAV)
        # -ar: sample rate (16000 Hz is optimal for Whisper)
        # -ac: audio channels (1 for mono)
        # -y: overwrite output file if exists
        # -progress: output progress information
        try:
            cmd = [self.ffmpeg_path, '-i', str(media_path)]
            logger.debug(f"Initial ffmpeg command: {cmd}")
            # Only add -vn for video files
            if self.is_video_file(media_path):
                cmd.append('-vn')  # No video
                logger.debug("Added '-vn' to ffmpeg command for video file")
            # Add audio processing options
            codec = 'pcm_s16le' if audio_format == 'wav' else 'libmp3lame'
            cmd.extend([
                '-acodec', codec,
                '-ar', '16000',  # Sample rate (Whisper works best with 16kHz)
                '-ac', '1',  # Mono audio
                '-y',  # Overwrite output
                output_path
            ])
            logger.debug(f"Final ffmpeg command: {cmd}")
            # OPTIMIZED: Show progress during extraction (though ffmpeg progress parsing
            # would require async processing, so we'll just show intermediate updates)
            if progress_callback:
                progress_callback(f"{action_present} audio... Processing", 15)
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logger.debug(f"ffmpeg stdout: {result.stdout.decode('utf-8', errors='ignore')}")
            logger.debug(f"ffmpeg stderr: {result.stderr.decode('utf-8', errors='ignore')}")
            if progress_callback:
                progress_callback(f"{action_present} audio... Finalizing", 25)
            if not os.path.exists(output_path):
                logger.error(f"Audio processing completed but output file not found: {output_path}")
                raise RuntimeError("Audio processing completed but output file not found")
            logger.info(f"Audio {action_past} successfully to {output_path}")
            if progress_callback:
                progress_callback(f"Audio {action_past} successfully", 30)
            return output_path
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8', errors='ignore')
            logger.error(f"ffmpeg error: {error_msg}")
            logger.error(f"ffmpeg command: {cmd}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Executable directory: {os.path.dirname(os.path.abspath(__file__))}")
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
                logger.debug(f"Attempting to delete temporary file: {file_path}")
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            else:
                logger.debug(f"Temporary file not found for cleanup: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")

