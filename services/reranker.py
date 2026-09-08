import gc
import os
import threading

from core.config import (
    RERANKER_MODEL,
    RERANK_TOP_K,
)


class CrossEncoderReranker:
    """
    Re-ranks retrieved chunks using a CrossEncoder model.
    """

    def __init__(self) -> None:
        self.model = None
        self._load_lock = threading.Lock()

    def _load_model(self) -> None:
        if self.model is not None:
            return

        with self._load_lock:
            if self.model is not None:
                return

            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            from sentence_transformers import CrossEncoder

            print(f"Loading reranker: {RERANKER_MODEL}")
            model = CrossEncoder(
                model_name=RERANKER_MODEL,
                device="cpu",
            )
            self.model = model
            print("CrossEncoder loaded.")

    def unload_model(self) -> None:
        if self.model is None:
            return

        del self.model
        self.model = None
        gc.collect()

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> list[dict]:

        if not retrieved_chunks:
            return []

        self._load_model()

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