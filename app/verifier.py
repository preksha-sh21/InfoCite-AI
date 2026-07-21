"""Verification heuristics for generated answers."""

from __future__ import annotations

from typing import Sequence


def verify_answer(answer: str, sources: Sequence[str]) -> dict:
    """Return a simple verification structure with a confidence score."""
    source_text = " ".join(sources).lower()
    answer_text = answer.lower()
    overlap = sum(1 for token in answer_text.split() if token in source_text.split())
    confidence = min(1.0, overlap / max(1, len(answer_text.split())))
    return {
        "confidence": round(confidence, 3),
        "has_sources": bool(sources),
        "verified": confidence >= 0.2,
    }
