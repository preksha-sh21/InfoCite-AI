"""
Embedding generation service.
"""

import gc
import os
import threading
from typing import List

from core.config import EMBEDDING_MODEL


class EmbeddingService:
    """
    Generates dense vector embeddings using Sentence Transformers.
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
            from sentence_transformers import SentenceTransformer

            print(f"Loading embedding model: {EMBEDDING_MODEL}")
            model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
            self.model = model
            print("Embedding model loaded successfully.")

    def unload_model(self) -> None:
        if self.model is None:
            return

        del self.model
        self.model = None
        gc.collect()

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """
        self._load_model()
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """
        self._load_model()
        embeddings = self.model.encode(
            texts,
            batch_size=min(batch_size, 8),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()