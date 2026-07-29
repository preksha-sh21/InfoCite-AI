import os

# Force CPU usage before importing torch/sentence-transformers
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from sentence_transformers import CrossEncoder

from core.config import (
    RERANKER_MODEL,
    RERANK_TOP_K,
)


class CrossEncoderReranker:
    """
    Re-ranks retrieved chunks using a CrossEncoder model.
    """

    def __init__(self) -> None:

        print(f"Loading reranker: {RERANKER_MODEL}")

        self.model = CrossEncoder(
            model_name=RERANKER_MODEL,
            device="cpu",
        )

        print("CrossEncoder loaded.")

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> list[dict]:

        if not retrieved_chunks:
            return []

        pairs = [
            (query, chunk["text"])
            for chunk in retrieved_chunks
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        for chunk, score in zip(retrieved_chunks, scores):
            chunk["cross_score"] = float(score)

        ranked = sorted(
            retrieved_chunks,
            key=lambda chunk: chunk["cross_score"],
            reverse=True,
        )

        return ranked[:RERANK_TOP_K]