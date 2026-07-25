from typing import Dict, List

from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.bm25 import BM25Retriever
from models.document_chunk import DocumentChunk


class HybridRetriever:
    """
    Combines semantic retrieval and BM25 retrieval using
    Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        vector_store: VectorStore,
        bm25: BM25Retriever,
        embedding_service: EmbeddingService,
    ) -> None:

        self.vector_store = vector_store
        self.bm25 = bm25
        self.embedding_service = embedding_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ):

        query_embedding = (
            self.embedding_service.generate_embedding(query)
        )

        vector_results = self.vector_store.query(
            query_embedding=query_embedding,
            top_k=top_k * 2,
        )

        bm25_results = self.bm25.search(
            query=query,
            top_k=top_k * 2,
        )

        return self._reciprocal_rank_fusion(
            vector_results,
            bm25_results,
            top_k,
        )

    def _reciprocal_rank_fusion(
        self,
        vector_results,
        bm25_results,
        top_k,
    ):

        rrf_scores: Dict[str, float] = {}

        metadata_lookup = {}

        documents = vector_results["documents"][0]
        metadatas = vector_results["metadatas"][0]

        for rank, (doc, meta) in enumerate(
            zip(documents, metadatas),
            start=1,
        ):

            key = (
                meta["source"],
                meta["page"],
                meta["chunk_index"],
            )

            rrf_scores[key] = (
                rrf_scores.get(key, 0)
                + 1 / (60 + rank)
            )

            metadata_lookup[key] = {
                "text": doc,
                "page": meta["page"],
                "source": meta["source"],
            }

        for rank, (_, chunk) in enumerate(
            bm25_results,
            start=1,
        ):

            key = (
                chunk.source,
                chunk.page_number,
                chunk.chunk_index,
            )

            rrf_scores[key] = (
                rrf_scores.get(key, 0)
                + 1 / (60 + rank)
            )

            metadata_lookup[key] = {
                "text": chunk.text,
                "page": chunk.page_number,
                "source": chunk.source,
            }

        ranked = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []

        for key, score in ranked[:top_k]:

            item = metadata_lookup[key]

            item["rrf_score"] = score

            results.append(item)

        return results