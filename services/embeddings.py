"""
Embedding generation service.
"""

from typing import List

from sentence_transformers import SentenceTransformer

from core.config import EMBEDDING_MODEL


class EmbeddingService:
    """
    Generates dense vector embeddings using Sentence Transformers.
    """

    def __init__(self) -> None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
            device="cpu",
        )

        print("Embedding model loaded successfully.")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """
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
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()