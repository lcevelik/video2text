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
from tools.resource_locator import get_ffmpeg_path, get_ffprobe_path

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extracts audio from video files or prepares audio files for transcription using ffmpeg."""

    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}

    # Supported audio formats (Whisper can handle these directly, but we may need to convert for optimal format)
    SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.opus', '.mp2'}

    # All supported formats
    SUPPORTED_FORMATS = SUPPORTED_VIDEO_FORMATS | SUPPORTED_AUDIO_FORMATS

    @staticmethod
    def configure_ffmpeg_converter():
        """
        Configure pydub to use an available ffmpeg binary without requiring shell restart.
        Checks bundled resources, system PATH, and common install locations.
        """
        try:
            import shutil
            import sys
            from pydub import AudioSegment
        except ImportError as e:
            logger.debug(f"Could not import dependencies for ffmpeg config: {e}")
            return

        # Check for bundled ffmpeg in macOS app package or PyInstaller bundle
        possible_ffmpeg_paths = []
        if hasattr(sys, 'frozen'):
            possible_ffmpeg_paths.append(os.path.join(sys._MEIPASS, 'ffmpeg')) # PyInstaller
            possible_ffmpeg_paths.append(os.path.join(os.path.dirname(sys.executable), 'ffmpeg'))

        possible_ffmpeg_paths.extend([
            os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'ffmpeg')),
            os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'Resources', 'ffmpeg')),
        ])

        # Try NSBundle for macOS app bundle launches
        if sys.platform == 'darwin':
            try:
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                resources_path = str(bundle.resourcePath())
                nsbundle_ffmpeg = os.path.join(resources_path, 'ffmpeg')
                possible_ffmpeg_paths.append(nsbundle_ffmpeg)
            except Exception:
                pass

        # Check potential paths
        for bundled_ffmpeg in possible_ffmpeg_paths:
            if os.path.exists(bundled_ffmpeg):
                try:
                    # Set for pydub
                    AudioSegment.converter = bundled_ffmpeg
                    # Set environment variable for subprocess calls (e.g. in audio_processing.py)
                    os.environ['FFMPEG_BINARY'] = bundled_ffmpeg
                    # Also assume ffprobe is in same dir
                    ffprobe_path = os.path.join(os.path.dirname(bundled_ffmpeg), 'ffprobe')
                    if os.path.exists(ffprobe_path):
                        os.environ['FFPROBE_BINARY'] = ffprobe_path
                    
                    logger.info(f"Configured ffmpeg at: {bundled_ffmpeg}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to set ffmpeg converter: {e}")

        # If ffmpeg is on PATH, set converter and return
        if shutil.which('ffmpeg'):
            try:
                AudioSegment.converter = 'ffmpeg'
                logger.info("Configured ffmpeg from PATH")
            except Exception:
                pass
            return

        # Try common install locations (Windows, Homebrew, MacPorts)
        candidates = [
            r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            r"C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe",
            str(Path.home() / "scoop" / "apps" / "ffmpeg" / "current" / "bin" / "ffmpeg.exe"),
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/local/bin/ffmpeg",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    AudioSegment.converter = p
                    os.environ['FFMPEG_BINARY'] = p
                    logger.info(f"Configured ffmpeg from common location: {p}")
                    return
                except Exception:
                    pass

    def __init__(self):
        """Initialize the AudioExtractor."""
        self.ffmpeg_path = None
        self.ffprobe_path = None
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is installed and accessible."""
        try:
            self.ffmpeg_path = get_ffmpeg_path()
            self.ffprobe_path = get_ffprobe_path()

            # Set environment variables for subprocess calls in transcription modules
            os.environ['FFMPEG_BINARY'] = self.ffmpeg_path
            os.environ['FFPROBE_BINARY'] = self.ffprobe_path

            # Test ffmpeg availability
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=5
            )
            logger.info(f"ffmpeg is available at: {self.ffmpeg_path}")
            logger.info(f"ffprobe is available at: {self.ffprobe_path}")
            
            # Check if using system ffmpeg (not bundled)
            import shutil
            system_ffmpeg = shutil.which('ffmpeg')
            if system_ffmpeg and os.path.samefile(self.ffmpeg_path, system_ffmpeg):
                logger.warning("⚠ Using system ffmpeg instead of bundled version. This is fine, but bundled version is preferred for DMG installations.")
        except subprocess.TimeoutExpired:
            logger.warning(f"ffmpeg version check timed out, but continuing anyway")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # If we got a path but it doesn't work, log warning but don't fail
            logger.warning(f"ffmpeg test failed: {e}, but path exists. Continuing anyway.")
        except RuntimeError as e:
            # Only raise if ffmpeg truly not found (no path at all)
            raise RuntimeError(
                f"ffmpeg is not available: {e}\n"
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
                self.ffprobe_path,
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
    
    def extract_audio(self, media_path, output_path=None, audio_format='ogg', progress_callback=None):
        """
        Extract or prepare audio from a media file (video or audio).
        - If input is a video file: extracts audio from video
        - If input is an audio file: converts to optimal format for Whisper (Opus/OGG at 16kHz mono)

        OPTIMIZED: Now uses Opus codec for smallest file size while maintaining transcription quality.
        Opus is the most efficient codec for speech transcription with Whisper.

        Args:
            media_path: Path to the input media file (video or audio)
            output_path: Path for the output audio file (optional)
            audio_format: Output audio format (default: 'ogg' for Opus)
            progress_callback: Optional callback function(message, percentage) for progress updates

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

        # Check if source is already optimal Opus/OGG format (16kHz mono)
        # Opus files are already optimal for Whisper, so we can use them directly
        if media_path.suffix.lower() == '.ogg':
            try:
                import soundfile as sf
                test_data, test_sr = sf.read(str(media_path))
                # Check if it's already 16kHz mono
                if test_sr == 16000 and (len(test_data.shape) == 1 or test_data.shape[1] == 1):
                    logger.info(f"Source OGG is already optimal format (16kHz mono), using directly")
                    return str(media_path)
            except Exception as e:
                logger.debug(f"Could not verify OGG format, will convert: {e}")
        
        # Also check WAV files that are already optimal
        if media_path.suffix.lower() == '.wav':
            try:
                import soundfile as sf
                test_data, test_sr = sf.read(str(media_path))
                # Check if it's already 16kHz mono
                if test_sr == 16000 and (len(test_data.shape) == 1 or test_data.shape[1] == 1):
                    logger.info(f"Source WAV is already optimal format (16kHz mono), using directly")
                    return str(media_path)
            except Exception as e:
                logger.debug(f"Could not verify WAV format, will convert: {e}")

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
            action_present = "Converting"
            action_past = "converted"
        else:
            logger.info(f"Extracting audio from video {media_path} to {output_path}")
            action_present = "Extracting"
            action_past = "extracted"

        if progress_callback:
            progress_callback(f"{action_present} audio...", 5)

        # Use ffmpeg to extract/convert audio to Opus/OGG format
        # Opus is the most efficient codec for speech transcription with Whisper
        # -i: input file
        # -vn: disable video (for video files)
        # -c:a: audio codec (libopus for OGG, pcm_s16le for WAV fallback)
        # -b:a: bitrate (18k for Opus - optimal for voice between 12-24k)
        # -ar: sample rate (16000 Hz is optimal for Whisper)
        # -ac: audio channels (1 for mono)
        # -application voip: optimize for voice/speech
        # -y: overwrite output file if exists
        try:
            cmd = [self.ffmpeg_path, '-i', str(media_path)]

            # Only add -vn for video files
            if self.is_video_file(media_path):
                cmd.append('-vn')  # No video

            # Add audio processing options
            if audio_format == 'ogg':
                # Use Opus codec with optimized settings for speech
                cmd.extend([
                    '-c:a', 'libopus',  # Opus codec
                    '-b:a', '18k',  # 18 kbps bitrate (optimal for voice)
                    '-ar', '16000',  # Sample rate (Whisper works best with 16kHz)
                    '-ac', '1',  # Mono audio
                    '-application', 'voip',  # Optimize for voice/speech
                    '-y',  # Overwrite output
                    output_path
                ])
            elif audio_format == 'wav':
                # Fallback to WAV if needed
                cmd.extend([
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',  # Sample rate (Whisper works best with 16kHz)
                    '-ac', '1',  # Mono audio
                    '-y',  # Overwrite output
                    output_path
                ])
            else:
                # Other formats (MP3, etc.)
                cmd.extend([
                    '-acodec', 'libmp3lame',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    output_path
                ])

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

            if progress_callback:
                progress_callback(f"{action_present} audio... Finalizing", 25)

            if not os.path.exists(output_path):
                raise RuntimeError("Audio processing completed but output file not found")
            
            # Validate extracted audio file is not empty
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise RuntimeError(f"Audio extraction produced an empty file (0 bytes). The source file may be corrupted or invalid.")
            
            # Check minimum file size (should be at least a few KB for valid audio)
            if file_size < 1024:  # Less than 1KB is suspicious
                logger.warning(f"Extracted audio file is very small ({file_size} bytes). This may indicate a problem.")
            
            # Try to validate audio file can be read
            try:
                import soundfile as sf
                test_data, test_sr = sf.read(output_path)
                if len(test_data) == 0:
                    raise RuntimeError("Extracted audio file contains no audio samples")
                logger.info(f"Audio validation: {len(test_data)} samples at {test_sr}Hz")
            except ImportError:
                logger.debug("soundfile not available, skipping audio validation")
            except Exception as e:
                logger.warning(f"Audio validation failed: {e}, but continuing anyway")

            logger.info(f"Audio {action_past} successfully to {output_path} (size: {file_size} bytes)")

            if progress_callback:
                progress_callback(f"Audio {action_past} successfully", 30)

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

