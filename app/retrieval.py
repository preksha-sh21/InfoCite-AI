"""Retrieval logic for ranking chunks against a query."""

from __future__ import annotations

from typing import List, Sequence, Tuple

from .embeddings import embed_query, embed_texts


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right:
        return 0.0

    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return float(numerator / (left_norm * right_norm))


def retrieve_documents(query: str, documents: Sequence[str], top_k: int = 5) -> List[Tuple[str, float]]:
    """Return the top matching documents with a similarity score."""
    if not documents:
        return []

    query_vector = embed_query(query)
    doc_vectors = embed_texts(list(documents))
    scored = [
        (document, _cosine_similarity(query_vector, vector))
        for document, vector in zip(documents, doc_vectors)
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]
