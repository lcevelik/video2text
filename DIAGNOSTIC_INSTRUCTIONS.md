I need to add diagnostic code to transcriber_enhanced.py. Since multi_replace had issues and apply_patch is disabled, I'll create a comprehensive patch script you can review. Run this after closing the app.

The changes are in 3 locations:

1. Constructor (DONE✓) - already updated with enable_diagnostics flag
2. Insert logging before/after merge in _retranscribe_segments_with_model (LINE ~388-398)
3. Add 3 new diagnostic methods at the end of the class (after format_multilang_report)

Here's what needs to be inserted at line 394 (before the merge call):

```python
        # DIAGNOSTIC: Log raw segments before any merging
        if hasattr(self, '_log_segment_diagnostics'):
            self._log_segment_diagnostics(language_segments, "RAW (before merge)")
        
        # Store raw segments for diagnostics
        if self.enable_diagnostics:
            self.diagnostics['raw_segments'] = [seg.copy() for seg in language_segments]
```

And after the merge (around line 398):

```python
        # DIAGNOSTIC: Log merged segments
        if hasattr(self, '_log_segment_diagnostics'):
            self._log_segment_diagnostics(merged_segments, "MERGED")
        
        # Store merged segments for diagnostics
        if self.enable_diagnostics:
            self.diagnostics['merged_segments'] = [seg.copy() for seg in merged_segments]
```

Then add these three methods at the end of the EnhancedTranscriber class (see transcriber_diagnostics_addon.py for the complete code).

Would you like me to:
A) Try a simpler grep-based edit approach?
B) Create a Python script to do the insertion automatically?
C) Guide you through manual edits with exact line numbers?
