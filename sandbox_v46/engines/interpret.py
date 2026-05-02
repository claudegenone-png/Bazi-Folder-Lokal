"""V4.6: DEAD CODE — DO NOT IMPORT.

Previous version (V4.6 draft) had ~416 lines of hardcoded narrative tables
(TEN_GOD_MATRIX, SI_HUA_*, MING_ZHU_NARRATIVE, etc.) used as a synthesizer
fallback when OCR didn't extract narrative paragraphs.

Per V4.6 FINAL audit (2026-05-02): synthesizer is forbidden — narrative MUST
come from photo OCR verbatim, or the relevant page is skipped (Task 5).

This file is a stub left in place because the sandbox cannot delete.
DO NOT add interpretation tables here. Re-running build_from_ocr.py will
verify nothing imports this module.
"""
