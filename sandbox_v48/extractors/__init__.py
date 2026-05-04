"""V4.8 Extractor pipeline.

Multi-strategy extraction: try strategies in priority order, fallback gracefully.
Each extractor takes raw MD text + return populated canonical sub-model or None.
"""
