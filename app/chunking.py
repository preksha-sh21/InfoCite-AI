"""Utilities for splitting text into smaller, processable chunks."""

from __future__ import annotations

from typing import List


def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks.

    The implementation is intentionally simple and dependency-free so it can be
    used as a baseline for later integration with more advanced chunking logic.
    """
    if not text:
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text.strip()]

    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start = max(0, end - overlap)

    return chunks
