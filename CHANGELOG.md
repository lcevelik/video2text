# Changelog

All notable changes to this project will be documented in this file.

## [v3.1.0] - 2025-11-15
### Added
- Deep Scan toggle (menu: Enable Deep Scan) for optional secondary chunk re-transcription.
- Expanded multi-language allow-list dialog (added PL, RU, ZH, JA, KO, AR and infrastructure for more).
- Cancellation support preserving partial transcript + language timeline.
- Performance overlay (progress %, elapsed time, ETA, final Real-Time Factor).
- Comprehensive documentation updates across README variants and implementation summary.
- CHANGELOG introduced.

### Changed
- Multi-language pipeline refactored: transcript-first heuristic segmentation now default (faster start, reduced redundant passes).
- Removed mandatory early sampling step when user declares multi-language.
- Fallback chunk analysis now conditional (only when heuristic collapses to single language in multi-mode).
- Language detection logic improved (enhanced English stopwords, Czech diacritic/common word density, allow-list filtering).

### Fixed
- Prior issues where English segments could be missed in Czech/English mixed audio.
- GUI errors from missing imports / cancellation attribute.
- Unintended UI clearing during multi-language dialog interactions.

### Performance
- Typical multi-language transcription speed improved by skipping initial sampling pass.
- Heuristic-only mode offers ~25–40% faster completion compared to legacy mandatory deep chunk double pass.
- Deep Scan optional for edge cases with rapid short code-switching.

### Notes
- Enable Deep Scan only if heuristic timeline boundaries appear merged or very short alternations are missing.
- Large model remains default for accuracy; detection leverages transcript heuristics over separate model pass.

---

## [Unreleased]
- Further language expansions
- Adaptive window sizing for heuristic segmentation
- Export of per-language confidence metrics

