"""Simple reranking helpers for retrieved passages."""

from __future__ import annotations

from typing import List, Sequence, Tuple


def rerank_documents(items: Sequence[Tuple[str, float]], top_k: int = 5) -> List[Tuple[str, float]]:
    """Return the highest-scoring items after a basic reranking pass."""
    scored = sorted(items, key=lambda item: item[1], reverse=True)
    return scored[:top_k]
