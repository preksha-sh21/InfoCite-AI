"""Simple embedding helpers for local experimentation."""

from __future__ import annotations

import hashlib
import math
from typing import List


def _token_vector(text: str, dimensions: int = 32) -> List[float]:
    """Create a deterministic, lightweight embedding-like vector."""
    vector = [0.0] * dimensions
    tokens = [token.lower() for token in text.replace("\n", " ").split() if token]
    if not tokens:
        return vector

    for index, token in enumerate(tokens):
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % dimensions
        vector[bucket] += 1.0 + (index % 5) * 0.1

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude:
        vector = [value / magnitude for value in vector]
    return vector


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of text strings."""
    return [_token_vector(text) for text in texts]


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return _token_vector(query)
