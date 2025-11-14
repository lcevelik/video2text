"""
Enhanced Transcription Module with Multi-Language Support

This module extends the base transcriber with:
- Multi-language segment detection
- Quality-based model selection
- Advanced language analysis
"""

import os
import logging
import tempfile
from typing import Dict, List, Optional, Any
from transcriber import Transcriber

logger = logging.getLogger(__name__)


class EnhancedTranscriber(Transcriber):
    """Enhanced transcriber with multi-language support."""

    # Common language code to name mapping
    LANGUAGE_NAMES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'pl': 'Polish',
        'nl': 'Dutch',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'he': 'Hebrew',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'tr': 'Turkish',
        'cs': 'Czech',
        'ro': 'Romanian',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'el': 'Greek',
        'hi': 'Hindi',
        'id': 'Indonesian',
        'uk': 'Ukrainian',
        'unknown': 'Unknown'
    }

    def __init__(self, model_size='base'):
        """
        Initialize the Enhanced Transcriber.

        Args:
            model_size: Size of the Whisper model to use
        """
        super().__init__(model_size)
        self.language_segments = []

    def transcribe_multilang(
        self,
        audio_path: str,
        detect_language_changes: bool = True,
        initial_prompt: Optional[str] = None,
        progress_callback=None,
        use_segment_retranscription: bool = True,
        detection_model: str = "base",
        transcription_model: str = "medium"
    ) -> Dict[str, Any]:
        """
        Transcribe audio with multi-language detection using two-pass approach.

        For TRUE multi-language support (code-switching), this method:
        1. PASS 1: Uses fast model (base) to detect segment boundaries and languages
        2. PASS 2: Uses accurate model (medium) to re-transcribe each segment
        3. Combines results with proper language labels

        This two-pass approach is faster and more accurate than using one large model.

        Args:
            audio_path: Path to the audio file
            detect_language_changes: Whether to detect language changes
            initial_prompt: Optional initial prompt
            progress_callback: Optional callback for progress updates
            use_segment_retranscription: If True, re-transcribe segments individually
            detection_model: Model for Pass 1 (default: "base" - fast detection)
            transcription_model: Model for Pass 2 (default: "medium" - accurate transcription)

        Returns:
            dict: Enhanced transcription result with language information
        """
        if detect_language_changes and use_segment_retranscription:
            # PASS 1: Fast detection using base model
            if progress_callback:
                progress_callback(f"Pass 1: Detecting languages with {detection_model} model...")

            # Create temporary transcriber with detection model
            from transcriber import Transcriber
            detection_transcriber = Transcriber(model_size=detection_model)

            # Quick pass to get segments and detect languages
            detection_result = detection_transcriber.transcribe(
                audio_path,
                language=None,  # Auto-detect
                initial_prompt=initial_prompt,
                progress_callback=None  # Don't spam progress
            )

            logger.info(f"Pass 1 complete: Detected {len(detection_result.get('segments', []))} segments")

            # PASS 2: Accurate transcription using transcription model per segment
            if progress_callback:
                progress_callback(f"Pass 2: Transcribing segments with {transcription_model} model...")

            self.language_segments = self._retranscribe_segments_with_model(
                audio_path,
                detection_result.get('segments', []),
                transcription_model,
                progress_callback
            )

            # Build result
            result = {}
            result['text'] = ' '.join(seg['text'] for seg in self.language_segments)
            result['segments'] = detection_result.get('segments', [])
            result['language'] = detection_result.get('language', 'unknown')
            result['language_segments'] = self.language_segments
            result['language_timeline'] = self._create_language_timeline(
                self.language_segments
            )

            logger.info(f"Pass 2 complete: Transcribed with {len(set(s['language'] for s in self.language_segments))} languages detected")

        else:
            # Single pass: use current model
            if progress_callback:
                progress_callback("Transcribing...")

            result = self.transcribe(
                audio_path,
                language=None,  # Auto-detect
                initial_prompt=initial_prompt,
                progress_callback=progress_callback
            )

            if detect_language_changes:
                # Fallback: use character-based detection (less accurate)
                self.language_segments = self._detect_language_segments(result)
                result['language_segments'] = self.language_segments
                result['language_timeline'] = self._create_language_timeline(
                    self.language_segments
                )

        return result

    def _retranscribe_segments(
        self,
        audio_path: str,
        segments: List[Dict[str, Any]],
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Re-transcribe each segment individually to detect its specific language.

        This is the KEY to true multi-language transcription. By transcribing
        each segment separately, Whisper can detect the correct language for that
        specific segment instead of assuming one language for the entire audio.

        Args:
            audio_path: Path to the full audio file
            segments: List of segments from initial transcription
            progress_callback: Optional callback for progress updates

        Returns:
            List of language segments with accurate per-segment language detection
        """
        import subprocess

        language_segments = []
        total_segments = len(segments)

        logger.info(f"Re-transcribing {total_segments} segments for accurate language detection")

        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            duration = end_time - start_time

            if duration < 0.1:  # Skip very short segments
                continue

            # Progress update
            if progress_callback and i % 5 == 0:  # Update every 5 segments
                progress_callback(f"Language detection: {i+1}/{total_segments} segments")

            try:
                # Extract audio segment using ffmpeg
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    temp_path = temp_audio.name

                # Use ffmpeg to extract the specific time range
                subprocess.run([
                    'ffmpeg', '-i', audio_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-ar', '16000',  # Whisper expects 16kHz
                    '-ac', '1',       # Mono
                    '-y',             # Overwrite
                    temp_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                # Transcribe this segment alone to detect its language
                segment_result = self.transcribe(
                    temp_path,
                    language=None,  # Auto-detect for THIS segment
                    progress_callback=None  # Don't spam progress for each segment
                )

                detected_lang = segment_result.get('language', 'unknown')
                transcribed_text = segment_result.get('text', '').strip()

                logger.debug(f"Segment {i}: {detected_lang} - {transcribed_text[:50]}...")

                # Add to our language segments
                language_segments.append({
                    'language': detected_lang,
                    'start': start_time,
                    'end': end_time,
                    'text': transcribed_text
                })

                # Clean up temp file
                os.unlink(temp_path)

            except Exception as e:
                logger.error(f"Failed to re-transcribe segment {i}: {e}")
                # Fallback: use original segment text with unknown language
                language_segments.append({
                    'language': 'unknown',
                    'start': start_time,
                    'end': end_time,
                    'text': segment.get('text', '').strip()
                })

        # Merge consecutive segments with the same language
        merged_segments = self._merge_consecutive_language_segments(language_segments)

        logger.info(f"Detected {len(set(s['language'] for s in merged_segments))} unique languages")

        return merged_segments

    def _merge_consecutive_language_segments(
        self,
        segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge consecutive segments that have the same language.

        Args:
            segments: List of language segments

        Returns:
            Merged list with consecutive same-language segments combined
        """
        if not segments:
            return []

        merged = []
        current = segments[0].copy()

        for segment in segments[1:]:
            if segment['language'] == current['language']:
                # Same language - merge with current
                current['end'] = segment['end']
                current['text'] += ' ' + segment['text']
            else:
                # Different language - save current and start new
                merged.append(current)
                current = segment.copy()

        # Add the last segment
        merged.append(current)

        return merged

    def _retranscribe_segments_with_model(
        self,
        audio_path: str,
        segments: List[Dict[str, Any]],
        model_name: str,
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Re-transcribe each segment individually using a SPECIFIC model.

        This is similar to _retranscribe_segments() but allows using a different
        model than the one this EnhancedTranscriber was initialized with.

        This is the KEY to the two-pass approach:
        - Pass 1 uses fast model (base) for detection
        - Pass 2 uses accurate model (medium) for transcription

        Args:
            audio_path: Path to the full audio file
            segments: List of segments from initial transcription
            model_name: Name of the model to use (e.g., "medium", "large")
            progress_callback: Optional callback for progress updates

        Returns:
            List of language segments with accurate per-segment transcription
        """
        import subprocess

        language_segments = []
        total_segments = len(segments)

        logger.info(f"Re-transcribing {total_segments} segments using {model_name} model")

        # Create a transcriber with the specified model
        transcriber = Transcriber(model_size=model_name)

        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            duration = end_time - start_time

            if duration < 0.1:  # Skip very short segments
                continue

            # Progress update
            if progress_callback and i % 5 == 0:  # Update every 5 segments
                progress_callback(f"Transcribing: {i+1}/{total_segments} segments ({model_name} model)")

            try:
                # Extract audio segment using ffmpeg
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    temp_path = temp_audio.name

                # Use ffmpeg to extract the specific time range
                subprocess.run([
                    'ffmpeg', '-i', audio_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-ar', '16000',  # Whisper expects 16kHz
                    '-ac', '1',       # Mono
                    '-y',             # Overwrite
                    temp_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                # Transcribe this segment alone to detect its language
                segment_result = transcriber.transcribe(
                    temp_path,
                    language=None,  # Auto-detect for THIS segment
                    progress_callback=None  # Don't spam progress for each segment
                )

                detected_lang = segment_result.get('language', 'unknown')
                transcribed_text = segment_result.get('text', '').strip()

                logger.debug(f"Segment {i}: {detected_lang} - {transcribed_text[:50]}...")

                # Add to our language segments
                language_segments.append({
                    'language': detected_lang,
                    'start': start_time,
                    'end': end_time,
                    'text': transcribed_text
                })

                # Clean up temp file
                os.unlink(temp_path)

            except Exception as e:
                logger.error(f"Failed to re-transcribe segment {i}: {e}")
                # Fallback: use original segment text with unknown language
                language_segments.append({
                    'language': 'unknown',
                    'start': start_time,
                    'end': end_time,
                    'text': segment.get('text', '').strip()
                })

        # Merge consecutive segments with the same language
        merged_segments = self._merge_consecutive_language_segments(language_segments)

        logger.info(f"Detected {len(set(s['language'] for s in merged_segments))} unique languages")

        return merged_segments

    def _detect_language_segments(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect language changes across segments.

        Args:
            result: Transcription result with segments

        Returns:
            List of language segments with timing
        """
        segments = result.get('segments', [])
        if not segments:
            return []

        # Get the language detected by Whisper
        whisper_detected_lang = result.get('language', 'unknown')
        logger.info(f"Whisper detected language: {whisper_detected_lang}")

        language_segments = []
        current_language = None
        current_start = None
        current_texts = []

        for segment in segments:
            text = segment.get('text', '').strip()
            start = segment.get('start', 0)
            end = segment.get('end', 0)

            # Use Whisper's detected language first, fallback to character-based heuristic
            # Whisper detects one language per audio, but we check for obvious script changes
            detected_lang = self._guess_language_from_text(text)

            # If character detection shows Latin script (defaults to 'en'), use Whisper's detection
            if detected_lang == 'en' and whisper_detected_lang != 'unknown':
                detected_lang = whisper_detected_lang

            if current_language is None:
                current_language = detected_lang
                current_start = start
                current_texts = [text]
            elif detected_lang != current_language:
                # Language changed
                language_segments.append({
                    'language': current_language,
                    'start': current_start,
                    'end': start,
                    'text': ' '.join(current_texts)
                })
                current_language = detected_lang
                current_start = start
                current_texts = [text]
            else:
                current_texts.append(text)

        # Add final segment
        if current_texts:
            language_segments.append({
                'language': current_language,
                'start': current_start,
                'end': segments[-1].get('end', 0),
                'text': ' '.join(current_texts)
            })

        logger.info(f"Detected {len(language_segments)} language segments")
        return language_segments

    def _guess_language_from_text(self, text: str) -> str:
        """
        Guess language from text using character patterns.

        Args:
            text: Text to analyze

        Returns:
            Guessed language code
        """
        if not text:
            return 'unknown'

        # Check for specific character ranges
        has_cjk = any('\u4e00' <= char <= '\u9fff' or
                      '\u3040' <= char <= '\u309f' or
                      '\u30a0' <= char <= '\u30ff' or
                      '\uac00' <= char <= '\ud7af' for char in text)

        has_arabic = any('\u0600' <= char <= '\u06ff' for char in text)
        has_cyrillic = any('\u0400' <= char <= '\u04ff' for char in text)
        has_hebrew = any('\u0590' <= char <= '\u05ff' for char in text)
        has_thai = any('\u0e00' <= char <= '\u0e7f' for char in text)

        if has_cjk:
            # Could be Chinese, Japanese, or Korean
            if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
                return 'ja'  # Japanese
            elif any('\uac00' <= char <= '\ud7af' for char in text):
                return 'ko'  # Korean
            else:
                return 'zh'  # Chinese
        elif has_arabic:
            return 'ar'
        elif has_cyrillic:
            return 'ru'
        elif has_hebrew:
            return 'he'
        elif has_thai:
            return 'th'
        else:
            # Default to Latin-based (could be any European language)
            return 'en'  # Default assumption

    def _create_language_timeline(
        self,
        language_segments: List[Dict[str, Any]]
    ) -> str:
        """
        Create a human-readable language timeline.

        Args:
            language_segments: List of language segments

        Returns:
            Formatted timeline string
        """
        timeline = []
        for segment in language_segments:
            start_str = self._format_timestamp_readable(segment['start'])
            end_str = self._format_timestamp_readable(segment['end'])
            lang_code = segment['language']
            lang_name = self.LANGUAGE_NAMES.get(lang_code, lang_code.upper())

            timeline.append(
                f"[{start_str} - {end_str}] Language: {lang_name} ({lang_code.upper()})"
            )

        return '\n'.join(timeline)

    def _format_timestamp_readable(self, seconds: float) -> str:
        """
        Format timestamp in readable format (MM:SS).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_quality_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate transcription quality score.

        Args:
            result: Transcription result

        Returns:
            Quality score (0.0 to 1.0)
        """
        segments = result.get('segments', [])
        if not segments:
            return 0.0

        total_confidence = 0.0
        count = 0

        for segment in segments:
            # Use no_speech_prob as quality indicator
            no_speech = segment.get('no_speech_prob', 0.0)
            confidence = 1.0 - no_speech

            # Also consider segment length (very short segments might be noise)
            duration = segment.get('end', 0) - segment.get('start', 0)
            text_length = len(segment.get('text', '').strip())

            # Penalize very short segments with little text
            if duration < 0.5 and text_length < 3:
                confidence *= 0.5

            total_confidence += confidence
            count += 1

        avg_confidence = total_confidence / count if count > 0 else 0.0

        logger.info(f"Calculated quality score: {avg_confidence:.3f}")
        return avg_confidence

    def format_as_vtt(self, transcription_result: Dict[str, Any]) -> str:
        """
        Format transcription result as VTT subtitle file.

        Args:
            transcription_result: Result dictionary from transcribe()

        Returns:
            str: VTT formatted subtitle content
        """
        segments = transcription_result.get('segments', [])
        vtt_content = ["WEBVTT\n"]

        for i, segment in enumerate(segments, start=1):
            start_time = self._format_vtt_timestamp(segment['start'])
            end_time = self._format_vtt_timestamp(segment['end'])
            text = segment['text'].strip()

            vtt_content.append(f"{start_time} --> {end_time}\n{text}\n")

        return "\n".join(vtt_content)

    def _format_vtt_timestamp(self, seconds: float) -> str:
        """
        Format seconds as VTT timestamp (HH:MM:SS.mmm).

        Args:
            seconds: Time in seconds

        Returns:
            str: Formatted VTT timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def format_multilang_report(self, result: Dict[str, Any]) -> str:
        """
        Format a detailed multi-language transcription report.

        Args:
            result: Enhanced transcription result with language info

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("MULTI-LANGUAGE TRANSCRIPTION REPORT")
        report.append("=" * 60)
        report.append("")

        # Overall info
        detected_lang = result.get('language', 'unknown')
        report.append(f"Primary Language: {detected_lang.upper()}")
        report.append("")

        # Language segments
        if 'language_segments' in result:
            segments = result['language_segments']
            report.append(f"Language Segments Detected: {len(segments)}")
            report.append("")

            for i, seg in enumerate(segments, 1):
                start_str = self._format_timestamp_readable(seg['start'])
                end_str = self._format_timestamp_readable(seg['end'])
                lang = seg['language']

                report.append(f"Segment {i}: {lang.upper()} [{start_str} - {end_str}]")
                report.append(f"  {seg['text'][:100]}...")
                report.append("")

        # Timeline
        if 'language_timeline' in result:
            report.append("Language Timeline:")
            report.append("-" * 60)
            report.append(result['language_timeline'])
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)
