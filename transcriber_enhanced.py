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
import time
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

    def __init__(self, model_size='base', enable_diagnostics=True):
        """
        Initialize the Enhanced Transcriber.

        Args:
            model_size: Size of the Whisper model to use
            enable_diagnostics: If True, save detailed diagnostic info to JSON
        """
        super().__init__(model_size)
        self.language_segments = []
        self.enable_diagnostics = enable_diagnostics
        self.diagnostics = {}  # Store diagnostic information
        self.cancel_requested = False  # User cancellation flag

    def transcribe_multilang(
        self,
        audio_path: str,
        detect_language_changes: bool = True,
        initial_prompt: Optional[str] = None,
        progress_callback=None,
        use_segment_retranscription: bool = True,
        detection_model: str = "base",
        transcription_model: str = "medium",
        skip_fast_single: bool = False,
        skip_sampling: bool = False,
        fast_text_language: bool = True,
        allowed_languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio with multi-language detection using word-level analysis.

        For TRUE multi-language support (code-switching), this method:
        1. Uses accurate model (medium) to transcribe with word timestamps
        2. Analyzes word-level language patterns to detect boundaries
        3. Groups words into language segments

        Args:
            audio_path: Path to the audio file
            detect_language_changes: Whether to detect language changes
            initial_prompt: Optional initial prompt
            progress_callback: Optional callback for progress updates
            use_segment_retranscription: If True, use word-level language detection
            detection_model: Deprecated (kept for compatibility)
            transcription_model: Model to use (default: "medium")

        Returns:
            dict: Enhanced transcription result with language information
        """
        if detect_language_changes and use_segment_retranscription:
            # Fast path: user forced multi-language, skip sampling classification entirely
            if skip_sampling:
                logger.info("Skipping sampling classification (forced multi-language mode).")
                if progress_callback:
                    progress_callback("Full word-level transcription (sampling skipped)...")
                result = self.transcribe(
                    audio_path,
                    language=None,
                    initial_prompt=initial_prompt,
                    word_timestamps=True,
                    progress_callback=progress_callback
                )
                if fast_text_language and not self.cancel_requested:
                    if progress_callback:
                        progress_callback("Fast transcript-based language segmentation...")
                    self.language_segments = self._detect_language_from_transcript(result.get('segments', []), chunk_size=4.0)
                    unique_langs = {s['language'] for s in self.language_segments}
                    if len(unique_langs) <= 1 and skip_fast_single and not self.cancel_requested:
                        logger.info("Transcript heuristic indicates single language; verifying with audio chunk pass...")
                        if progress_callback:
                            progress_callback("Verifying with audio chunks...")
                        self.language_segments = self._detect_language_from_words(audio_path, result.get('segments', []), progress_callback)
                else:
                    self.language_segments = self._detect_language_from_words(audio_path, result.get('segments', []), progress_callback)
                result['text'] = ' '.join(seg['text'] for seg in self.language_segments)
                result['language_segments'] = self.language_segments
                result['language_timeline'] = self._create_language_timeline(self.language_segments)
                result['classification'] = {'mode': 'forced-multilang'}
                if allowed_languages:
                    result['allowed_languages'] = allowed_languages
                return result
            # Sampling-based classification (single / mixed / hybrid)
            if progress_callback:
                progress_callback("Sampling audio for language classification...")
            sample_records, total_duration = self._sample_languages(audio_path, progress_callback=progress_callback)
            classification = self._classify_language_mode(sample_records, total_duration)
            logger.info(f"Language mode: {classification['mode']} | primary={classification['primary_language']} secondary={classification.get('secondary_languages')}")

            if classification['mode'] == 'single' and not skip_fast_single:
                # Fast path (only if not explicitly skipped)
                if progress_callback:
                    progress_callback(f"Single language detected ({classification['primary_language']}). Fast transcription...")
                result = self.transcribe(
                    audio_path,
                    language=classification['primary_language'],
                    initial_prompt=initial_prompt,
                    word_timestamps=False,
                    progress_callback=progress_callback
                )
                detected_lang = classification['primary_language'] or result.get('language', 'unknown')
                self.language_segments = [{
                    'language': detected_lang,
                    'start': 0,
                    'end': result.get('segments', [{}])[-1].get('end', 0) if result.get('segments') else 0,
                    'text': result.get('text', '')
                }]
                result['language_segments'] = self.language_segments
                result['language_timeline'] = self._create_language_timeline(self.language_segments)
                result['classification'] = classification
                if allowed_languages:
                    result['allowed_languages'] = allowed_languages
                logger.info("Fast mode complete (single language)")
                return result
            elif classification['mode'] == 'single' and skip_fast_single:
                logger.info("User forced multi-language mode; bypassing fast single-language path.")
                if progress_callback:
                    progress_callback("Bypassing single-language fast path; performing full word-level analysis...")

            # For now treat both mixed & hybrid with full multi-language pass (future optimization: partial reprocess for hybrid)
            if progress_callback:
                progress_callback("Multi-language mode: full word-level transcription...")
            result = self.transcribe(
                audio_path,
                language=None,  # Auto-detect all languages
                initial_prompt=initial_prompt,
                word_timestamps=True,  # Enable word-level timestamps
                progress_callback=progress_callback
            )

            logger.info(f"Transcription complete: {len(result.get('segments', []))} segments")
            
            # Analyze word-level language changes
            if progress_callback:
                progress_callback("Analyzing language changes...")
            
            self.language_segments = self._detect_language_from_words(
                audio_path,
                result.get('segments', []),
                progress_callback
            )

            # Build enhanced result
            result['text'] = ' '.join(seg['text'] for seg in self.language_segments)
            result['language_segments'] = self.language_segments
            result['language_timeline'] = self._create_language_timeline(self.language_segments)
            if allowed_languages:
                result['allowed_languages'] = allowed_languages

            logger.info(f"Language analysis complete: {len(set(s['language'] for s in self.language_segments))} languages detected")
            
            # DIAGNOSTIC: Save diagnostics to file if enabled
            if self.enable_diagnostics:
                self.diagnostics['raw_segments'] = self.language_segments.copy()
                self.diagnostics['merged_segments'] = self.language_segments.copy()
                self._save_diagnostics(audio_path)

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
                result['language_timeline'] = self._create_language_timeline(self.language_segments)
                if allowed_languages:
                    result['allowed_languages'] = allowed_languages

        return result

    def _detect_language_from_transcript(self, segments: List[Dict[str, Any]], chunk_size: float = 4.0) -> List[Dict[str, Any]]:
        """Heuristic segmentation using existing segment text (no extra audio passes).

        Improvements:
        - Larger English stopword list for better low-diacritic detection
        - Czech detection via diacritic density and common words
        - Allowed-language enforcement & remapping
        - Merge adjacent identical languages
        - Fallback propagation: short unknown windows inherit previous language
        """
        if not segments:
            return []
        end_time = segments[-1].get('end', 0)
        windows = []
        t = 0.0
        while t < end_time:
            windows.append((t, min(t + chunk_size, end_time)))
            t += chunk_size
        # Expanded English stopwords (common function/content words)
        en_stops = {
            "the","and","is","are","to","of","in","that","for","you","it","on","with","this","be","have","at","or","as","i","we","they","was","were","will","would","can","could","a","an","from","by","about","what","which","who","how","do","does","did","not","if","there","their","them","our","your"
        }
        cs_diacritics = set("áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ")
        cs_common = {"že","který","jsem","jsme","není","může","proto","tak","ale","by","když","už","je","co","jak"}
        allowed = getattr(self, 'allowed_languages', None)
        classified = []
        seg_index = 0
        prev_lang = None
        for (ws, we) in windows:
            texts = []
            idx = seg_index
            while idx < len(segments) and segments[idx].get('start', 0) < we:
                if segments[idx].get('end', 0) > ws:
                    texts.append(segments[idx].get('text', ''))
                idx += 1
            seg_index = idx
            window_text = ' '.join(texts).strip()
            if not window_text:
                continue
            lower = window_text.lower()
            words = [w.strip(".,!?;:") for w in lower.split() if w.strip()]
            if not words:
                continue
            cs_diacritic_count = sum(ch in cs_diacritics for ch in window_text)
            en_stop_hits = sum(1 for w in words if w in en_stops)
            cs_common_hits = sum(1 for w in words if w in cs_common)
            total_words = len(words)
            en_ratio = en_stop_hits / max(total_words,1)
            cs_ratio = (cs_common_hits + cs_diacritic_count*0.5) / max(total_words,1)
            # Language decision heuristics
            if cs_diacritic_count >= 2 or cs_ratio > en_ratio * 1.1:
                lang = 'cs'
            elif en_stop_hits >= 2 and en_ratio >= 0.05:
                lang = 'en'
            else:
                # Fallback: if high ascii and previous language exists, inherit
                lang = prev_lang if prev_lang else ('en' if en_ratio >= cs_ratio else 'cs')
            prev_lang = lang
            # Enforce allow-list
            if allowed and lang not in allowed:
                if len(allowed) == 1:
                    lang = allowed[0]
                elif len(allowed) == 2 and set(allowed) == {'en','cs'}:
                    # Re-evaluate quickly for en vs cs forced mapping
                    lang = 'cs' if cs_diacritic_count >= 1 or cs_common_hits >= 1 else 'en'
                else:
                    lang = 'unknown'
            classified.append({'language': lang, 'start': ws, 'end': we, 'text': window_text})
        # Merge adjacent same-language windows
        merged = []
        for seg in classified:
            if merged and merged[-1]['language'] == seg['language']:
                merged[-1]['end'] = seg['end']
                merged[-1]['text'] += ' ' + seg['text']
            else:
                merged.append(seg)
        logger.info(f"Fast transcript-based segmentation produced {len(merged)} segments (languages: {sorted({m['language'] for m in merged})})")
        return merged

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

        # DIAGNOSTIC: Log raw segments before any merging
        if hasattr(self, '_log_segment_diagnostics'):
            self._log_segment_diagnostics(language_segments, "RAW (before merge)")
        
        # Store raw segments for diagnostics
        if self.enable_diagnostics:
            if 'raw_segments' not in self.diagnostics:
                self.diagnostics['raw_segments'] = [seg.copy() for seg in language_segments]

        # Merge consecutive segments with the same language
        merged_segments = self._merge_consecutive_language_segments(language_segments)

        # DIAGNOSTIC: Log merged segments
        if hasattr(self, '_log_segment_diagnostics'):
            self._log_segment_diagnostics(merged_segments, "MERGED")
        
        # Store merged segments for diagnostics
        if self.enable_diagnostics:
            if 'merged_segments' not in self.diagnostics:
                self.diagnostics['merged_segments'] = [seg.copy() for seg in merged_segments]

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

        # DIAGNOSTIC: Log raw segments before any merging
        if hasattr(self, '_log_segment_diagnostics'):
            self._log_segment_diagnostics(language_segments, "RAW (before merge)")
        
        # Store raw segments for diagnostics
        if self.enable_diagnostics:
            self.diagnostics['raw_segments'] = [seg.copy() for seg in language_segments]

        # Merge consecutive segments with the same language
        merged_segments = self._merge_consecutive_language_segments(language_segments)

        # DIAGNOSTIC: Log merged segments
        if hasattr(self, '_log_segment_diagnostics'):
            self._log_segment_diagnostics(merged_segments, "MERGED")
        
        # Store merged segments for diagnostics
        if self.enable_diagnostics:
            self.diagnostics['merged_segments'] = [seg.copy() for seg in merged_segments]

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
            return 'en'

    def _sample_languages(self, audio_path: str, sample_window: float = 4.0, max_samples: int = 25, min_interval: float = 300.0, progress_callback=None):
        """Sample the audio at intervals to estimate language distribution.

        Returns (sample_records, total_duration)
        sample_records: List[{'time': seconds, 'language': str}]
        """
        import subprocess, math, tempfile, os
        # Get total duration
        try:
            ffprobe_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
            ]
            duration_output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT)
            total_duration = float(duration_output.decode().strip())
        except Exception as e:
            logger.warning(f"Duration probe failed: {e}; falling back to single sample")
            total_duration = 0
        if total_duration <= 0:
            # Single probe at start only
            temp_sample = tempfile.NamedTemporaryFile(delete=False, suffix='.wav'); temp_sample.close()
            try:
                ffmpeg_cmd = ['ffmpeg','-y','-i',audio_path,'-t',str(sample_window),'-ar','16000','-ac','1',temp_sample.name]
                subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
                r = self.transcribe(temp_sample.name, language=None, word_timestamps=False)
                return ([{'time':0.0,'language':r.get('language','unknown')}], 0.0)
            finally:
                if os.path.exists(temp_sample.name): os.unlink(temp_sample.name)

        # Determine sampling interval
        interval = min(min_interval, max(sample_window, total_duration / 12.0))
        points = []
        # Always include early (skip first 1.5s), middle, near end windows
        points.append(1.5)
        pos = interval
        while pos < total_duration - sample_window and len(points) < max_samples - 2:
            points.append(pos)
            pos += interval
        # Ensure middle
        mid = total_duration / 2.0
        if all(abs(p - mid) > sample_window for p in points):
            points.append(mid)
        # Tail samples
        tail1 = max(total_duration - sample_window - 2, 0)
        tail2 = max(total_duration - sample_window - interval/2, 0)
        for t in [tail2, tail1]:
            if all(abs(p - t) > sample_window/2 for p in points):
                points.append(t)
        # Sort & trim
        points = sorted(set(p for p in points if p < total_duration))[:max_samples]

        sample_records = []
        import tempfile, os
        for idx, start_time in enumerate(points):
            temp_sample = tempfile.NamedTemporaryFile(delete=False, suffix='.wav'); temp_sample.close()
            try:
                ffmpeg_cmd = [
                    'ffmpeg','-y','-i',audio_path,
                    '-ss',str(start_time),
                    '-t',str(sample_window),
                    '-ar','16000','-ac','1',temp_sample.name
                ]
                subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
                if progress_callback:
                    progress_callback(f"Language sampling {idx+1}/{len(points)} @ {start_time:.0f}s")
                r = self.transcribe(temp_sample.name, language=None, word_timestamps=False)
                lang = r.get('language','unknown')
                sample_records.append({'time': start_time, 'language': lang})
                logger.debug(f"Sample {idx+1}: t={start_time:.1f}s lang={lang}")
            except Exception as e:
                logger.warning(f"Sample failed at {start_time:.1f}s: {e}")
            finally:
                if os.path.exists(temp_sample.name): os.unlink(temp_sample.name)
        return sample_records, total_duration

    def _classify_language_mode(self, samples, total_duration: float, late_ratio: float = 0.85, min_secondary_hits: int = 2):
        """Classify language mode based on samples.

        Returns dict with keys: mode (single|mixed|hybrid), primary_language, secondary_languages, transition_time
        hybrid means second language appears only late (after late_ratio * duration).
        """
        if not samples:
            return {'mode':'single','primary_language':None,'secondary_languages':[], 'transition_time':None}
        # Tally languages
        from collections import Counter
        langs = [s['language'] for s in samples]
        counts = Counter(langs)
        primary = counts.most_common(1)[0][0]
        secondary_candidates = [l for l in counts if l != primary]
        if not secondary_candidates:
            return {'mode':'single','primary_language':primary,'secondary_languages':[], 'transition_time':None}
        # Verify secondary hits
        valid_secondaries = []
        earliest_secondary_time = None
        for sec in secondary_candidates:
            hits = [s for s in samples if s['language']==sec]
            if len(hits) >= min_secondary_hits:
                valid_secondaries.append(sec)
                tmin = min(h['time'] for h in hits)
                if earliest_secondary_time is None or tmin < earliest_secondary_time:
                    earliest_secondary_time = tmin
        if not valid_secondaries:
            # Treat as single if secondaries too sparse
            return {'mode':'single','primary_language':primary,'secondary_languages':[], 'transition_time':None}
        # Decide hybrid vs mixed
        if earliest_secondary_time and total_duration>0 and earliest_secondary_time/total_duration >= late_ratio:
            mode = 'hybrid'
        else:
            mode = 'mixed'
        return {
            'mode': mode,
            'primary_language': primary,
            'secondary_languages': valid_secondaries,
            'transition_time': earliest_secondary_time
        }

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

    def _log_segment_diagnostics(self, segments: List[Dict[str, Any]], stage: str):
        """
        Log detailed segment diagnostics for debugging multi-language detection.
        
        Args:
            segments: List of language segments
            stage: Description of processing stage (e.g., "RAW", "MERGED")
        """
        if not segments:
            logger.info(f"[DIAGNOSTIC {stage}] No segments")
            return
            
        # Count languages
        lang_counts = {}
        total_duration = 0
        for seg in segments:
            lang = seg['language']
            duration = seg['end'] - seg['start']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            total_duration += duration
        
        # Log summary
        logger.info(f"[DIAGNOSTIC {stage}] Total segments: {len(segments)}")
        logger.info(f"[DIAGNOSTIC {stage}] Languages detected: {list(lang_counts.keys())}")
        
        # Log per-language breakdown
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
            lang_name = self.LANGUAGE_NAMES.get(lang, lang.upper())
            percentage = (count / len(segments)) * 100
            logger.info(f"[DIAGNOSTIC {stage}]   {lang_name} ({lang}): {count} segments ({percentage:.1f}%)")
        
        # Log first few segments as examples
        logger.info(f"[DIAGNOSTIC {stage}] First 5 segments:")
        for i, seg in enumerate(segments[:5]):
            start_str = self._format_timestamp_readable(seg['start'])
            end_str = self._format_timestamp_readable(seg['end'])
            text_preview = seg['text'][:60].replace('\n', ' ')
            logger.info(f"[DIAGNOSTIC {stage}]   [{start_str}-{end_str}] {seg['language']}: {text_preview}...")

    def _save_diagnostics(self, audio_path: str):
        """
        Save comprehensive diagnostics to JSON file for analysis.
        
        Args:
            audio_path: Path to the audio file being transcribed
        """
        import json
        from pathlib import Path
        
        # Create diagnostics directory
        diag_dir = Path("diagnostics")
        diag_dir.mkdir(exist_ok=True)
        
        # Generate filename based on audio file
        audio_name = Path(audio_path).stem
        diag_file = diag_dir / f"{audio_name}_diagnostics.json"
        
        # Calculate statistics
        raw_segments = self.diagnostics.get('raw_segments', [])
        merged_segments = self.diagnostics.get('merged_segments', [])
        
        # Language statistics for raw segments
        raw_lang_stats = self._calculate_language_stats(raw_segments)
        merged_lang_stats = self._calculate_language_stats(merged_segments)
        
        # Build diagnostic data
        diagnostic_data = {
            "audio_file": str(audio_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pass1_info": {
                "detected_language": self.diagnostics.get('pass1_language', 'unknown'),
                "total_segments": len(self.diagnostics.get('pass1_segments', [])),
                "segments_sample": [
                    {
                        "start": seg.get('start', 0),
                        "end": seg.get('end', 0),
                        "text": seg.get('text', '')[:100]
                    }
                    for seg in self.diagnostics.get('pass1_segments', [])[:5]
                ]
            },
            "statistics": {
                "raw_segments": {
                    "total_count": len(raw_segments),
                    "languages_detected": list(raw_lang_stats.keys()),
                    "language_breakdown": raw_lang_stats
                },
                "merged_segments": {
                    "total_count": len(merged_segments),
                    "languages_detected": list(merged_lang_stats.keys()),
                    "language_breakdown": merged_lang_stats,
                    "segments_merged": len(raw_segments) - len(merged_segments)
                }
            },
            "raw_segments": raw_segments,
            "merged_segments": merged_segments
        }
        
        # Save to file
        try:
            with open(diag_file, 'w', encoding='utf-8') as f:
                json.dump(diagnostic_data, f, indent=2, ensure_ascii=False)
            logger.info(f"[DIAGNOSTIC] Saved detailed diagnostics to: {diag_file}")
            logger.info(f"[DIAGNOSTIC] Review this file to see exactly what was detected and merged")
        except Exception as e:
            logger.error(f"Failed to save diagnostics: {e}")
    
    def _calculate_language_stats(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate detailed statistics for language segments.
        
        Args:
            segments: List of language segments
            
        Returns:
            Dictionary with language statistics
        """
        if not segments:
            return {}
            
        stats = {}
        total_duration = sum(seg['end'] - seg['start'] for seg in segments)
        
        for seg in segments:
            lang = seg['language']
            lang_name = self.LANGUAGE_NAMES.get(lang, lang.upper())
            duration = seg['end'] - seg['start']
            
            if lang not in stats:
                stats[lang] = {
                    "language_name": lang_name,
                    "segment_count": 0,
                    "total_duration_seconds": 0,
                    "percentage_by_count": 0,
                    "percentage_by_duration": 0
                }
            
            stats[lang]["segment_count"] += 1
            stats[lang]["total_duration_seconds"] += duration
        
        # Calculate percentages
        total_segments = len(segments)
        for lang in stats:
            stats[lang]["percentage_by_count"] = (stats[lang]["segment_count"] / total_segments) * 100
            if total_duration > 0:
                stats[lang]["percentage_by_duration"] = (stats[lang]["total_duration_seconds"] / total_duration) * 100
        
        return stats

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
    def _detect_mixed_languages(self, audio_path, progress_callback=None):
        """
        Quick detection to determine if audio contains multiple languages.
        Samples 3 points in the audio (beginning, middle, end) and checks if languages differ.
        Returns True if mixed languages detected, False if single language.
        """
        import subprocess
        import tempfile
        import os
        
        try:
            # Get total duration using ffprobe
            ffprobe_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
            ]
            duration_output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT)
            total_duration = float(duration_output.decode().strip())
            
            if total_duration < 10:
                # Too short to sample - assume single language
                logger.info(f"Audio too short ({total_duration}s) for language sampling - assuming single language")
                return False
            
            # Sample 3 segments: start (2-5s), middle, end (last 3s before end)
            sample_duration = 3.0
            sample_points = [
                2.0,  # Start at 2s to skip any intro noise
                total_duration / 2,  # Middle
                max(total_duration - 5.0, total_duration / 2 + 5)  # Near end
            ]
            
            detected_languages = set()
            
            for i, start_time in enumerate(sample_points):
                # Extract sample segment
                temp_sample = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_sample.close()
                
                try:
                    ffmpeg_cmd = [
                        'ffmpeg', '-y', '-i', audio_path,
                        '-ss', str(start_time),
                        '-t', str(sample_duration),
                        '-ar', '16000', '-ac', '1',
                        temp_sample.name
                    ]
                    subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
                    
                    # Transcribe sample with medium model for accurate detection
                    if progress_callback:
                        progress_callback(f"Sampling audio ({i+1}/3)...")
                    
                    sample_result = self.transcribe(temp_sample.name, language=None, word_timestamps=False)
                    detected_lang = sample_result.get('language', 'unknown')
                    detected_languages.add(detected_lang)
                    
                    logger.info(f"Sample {i+1} at {start_time:.1f}s: {detected_lang}")
                    
                finally:
                    if os.path.exists(temp_sample.name):
                        os.unlink(temp_sample.name)
                
                # Early exit if we find multiple languages
                if len(detected_languages) > 1:
                    logger.info(f"Multiple languages detected: {detected_languages}")
                    return True
            
            logger.info(f"Single language detected across all samples: {detected_languages}")
            return False
            
        except Exception as e:
            logger.warning(f"Error during language detection sampling: {e}")
            # On error, assume mixed languages to use the safer chunk-based approach
            return True


    def _detect_language_from_words(
        self,
        audio_path: str,
        segments: List[Dict[str, Any]],
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Detect language changes at word level by re-transcribing small chunks.
        
        Args:
            audio_path: Path to the audio file
            segments: List of segments with word timestamps from main transcription
            progress_callback: Optional progress callback
            
        Returns:
            List of language segments with detected languages
        """
        import subprocess
        
        logger.info(f"Splitting audio into chunks for language detection...")
        
        # Get ACTUAL audio file duration using ffprobe
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            total_duration = float(result.stdout.strip())
            logger.info(f"Actual audio duration: {total_duration:.2f}s")
        except Exception as e:
            logger.warning(f"Failed to get audio duration via ffprobe: {e}, using segments")
            total_duration = segments[-1]['end'] if segments else 0
        
        chunk_size = 4.0  # Larger chunks (4s) for speed - medium model is accurate enough
        
        # Create time-based chunks
        chunks = []
        current_time = 0
        while current_time < total_duration:
            chunk_end = min(current_time + chunk_size, total_duration)
            chunks.append({'start': current_time, 'end': chunk_end})
            current_time = chunk_end
        
        logger.info(f"Created {len(chunks)} chunks from {total_duration:.1f}s audio")
        
        # Now detect language for each chunk
        language_segments = []
        
        start_time_perf = time.time()
        for i, chunk in enumerate(chunks):
            if self.cancel_requested:
                logger.info("Cancellation requested. Stopping language chunk processing early.")
                if progress_callback:
                    progress_callback("PROGRESS:100:Canceled - partial result")
                break
            start_time = chunk['start']
            end_time = chunk['end']
            duration = end_time - start_time
            
            # Skip very short chunks
            if duration < 0.3:
                continue
            
            if progress_callback:
                progress = int((i / max(len(chunks),1)) * 100)
                progress_callback(f"PROGRESS:{progress}:Chunk {i+1}/{len(chunks)} [{start_time:.1f}-{end_time:.1f}s]")
            
            try:
                # Extract this speech segment
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    temp_path = temp_audio.name
                
                # Extract audio segment
                subprocess.run([
                    'ffmpeg', '-i', audio_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    temp_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                
                # Use the main medium model for both detection AND transcription
                # This is more accurate than using separate models
                # First pass: detect language (auto-detect)
                segment_result = self.transcribe(
                    temp_path,
                    language=None,  # Auto-detect language
                    word_timestamps=False
                )
                
                detected_lang = segment_result.get('language', 'unknown')
                # Enforce allow-list if provided
                if hasattr(self, 'allowed_languages') and self.allowed_languages:
                    if detected_lang not in self.allowed_languages:
                        # Simple heuristic: if only one allowed, use it; else mark unknown
                        if len(self.allowed_languages) == 1:
                            detected_lang = self.allowed_languages[0]
                        else:
                            detected_lang = 'unknown'
                chunk_transcribed_text = segment_result.get('text', '').strip()
                
                # Skip if no speech detected in this chunk
                if not chunk_transcribed_text:
                    logger.info(f"Chunk {i+1}/{len(chunks)} [{start_time:.1f}-{end_time:.1f}s]: No speech detected, skipping")
                    os.unlink(temp_path)
                    continue
                
                # Use the transcribed text from THIS chunk
                language_segments.append({
                    'language': detected_lang,
                    'start': start_time,
                    'end': end_time,
                    'text': chunk_transcribed_text
                })
                
                logger.info(f"Chunk {i+1}/{len(chunks)} [{start_time:.1f}-{end_time:.1f}s]: {detected_lang} - {chunk_transcribed_text[:50]}...")
                
                os.unlink(temp_path)
                
            except Exception as e:
                logger.warning(f"Failed to detect language for chunk {i} [{start_time:.1f}-{end_time:.1f}s]: {e}")
        
        # Merge consecutive segments with the same language
        merged_segments = self._merge_consecutive_language_segments(language_segments)
        
        logger.info(f"Detected {len(merged_segments)} language segments from {len(language_segments)} chunks")
        total_time = time.time() - start_time_perf
        if progress_callback and not self.cancel_requested:
            progress_callback("PROGRESS:100:Language detection complete")
        logger.info(f"Language detection runtime: {total_time:.2f}s (chunks processed: {len(language_segments)})")
        
        return merged_segments

    def request_cancel(self):
        """Set cancellation flag to stop chunk loop early."""
        self.cancel_requested = True
    
    def _fallback_segment_detection(
        self,
        audio_path: str,
        segments: List[Dict[str, Any]],
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Fallback: detect language for each segment individually.
        
        Args:
            audio_path: Path to audio file
            segments: List of segments
            progress_callback: Optional progress callback
            
        Returns:
            List of language segments
        """
        import subprocess
        
        language_segments = []
        total_segments = len(segments)
        
        logger.info(f"Fallback: Detecting language for {total_segments} segments")
        
        for i, segment in enumerate(segments):
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            duration = end_time - start_time
            
            if duration < 0.1:
                continue
            
            if progress_callback and i % 5 == 0:
                progress_callback(f"Language detection: {i+1}/{total_segments}")
            
            try:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    temp_path = temp_audio.name
                
                subprocess.run([
                    'ffmpeg', '-i', audio_path,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    temp_path
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                
                result = self.transcribe(
                    temp_path,
                    language=None,
                    word_timestamps=False
                )
                
                language_segments.append({
                    'language': result.get('language', 'unknown'),
                    'start': start_time,
                    'end': end_time,
                    'text': segment.get('text', '')
                })
                
                os.unlink(temp_path)
                
            except Exception as e:
                logger.warning(f"Failed to detect language for segment {i}: {e}")
        
        merged_segments = self._merge_consecutive_language_segments(language_segments)
        
        return merged_segments
