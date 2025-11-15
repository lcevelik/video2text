# Diagnostic methods to be added to transcriber_enhanced.py
# Copy these methods into the EnhancedTranscriber class

def _log_segment_diagnostics(self, segments, stage):
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

def _save_diagnostics(self, audio_path):
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

def _calculate_language_stats(self, segments):
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
