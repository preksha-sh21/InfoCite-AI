from sentence_transformers import CrossEncoder

from core.config import (
    RERANKER_MODEL,
    RERANK_TOP_K,
)


class CrossEncoderReranker:
    """
    Re-ranks retrieved chunks using a CrossEncoder.
    """

    def __init__(self) -> None:

        print(f"Loading reranker: {RERANKER_MODEL}")

        self.model = CrossEncoder(
            RERANKER_MODEL
        )

        print("CrossEncoder loaded.")

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> list[dict]:

        pairs = [
            (
                query,
                chunk["text"],
            )
            for chunk in retrieved_chunks
        ]

        scores = self.model.predict(
            pairs
        )

        for chunk, score in zip(
            retrieved_chunks,
            scores,
        ):
            chunk["cross_score"] = float(score)

        ranked = sorted(
            retrieved_chunks,
            key=lambda x: x["cross_score"],
            reverse=True,
        )

        return ranked[:RERANK_TOP_K]