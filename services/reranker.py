import re

from core.config import (
    RERANK_TOP_K,
)


class LexicalReranker:
    """
    Reranks retrieved chunks using query term coverage.

    This lightweight lexical scorer is not a neural cross-encoder. It is kept
    dependency-free and exposes its score as a retrieval signal, not calibrated
    answer confidence.
    """

    def __init__(self) -> None:
        self.model = None

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> list[dict]:

        if not retrieved_chunks:
            return []

        query_terms = set(re.findall(r"\w+", query.lower()))

        for chunk in retrieved_chunks:
            chunk_terms = set(re.findall(r"\w+", chunk["text"].lower()))
            matched_terms = query_terms.intersection(chunk_terms)
            chunk["lexical_score"] = (
                len(matched_terms) / len(query_terms)
                if query_terms
                else 0.0
            )

        ranked = sorted(
            retrieved_chunks,
            key=lambda chunk: chunk["lexical_score"],
            reverse=True,
        )

        return ranked[:RERANK_TOP_K]
