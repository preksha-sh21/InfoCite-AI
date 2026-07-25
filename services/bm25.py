"""
BM25 keyword retrieval service.
"""

from typing import List

from rank_bm25 import BM25Okapi

from models.document_chunk import DocumentChunk


class BM25Retriever:
    """
    Performs keyword-based retrieval using BM25.
    """

    def __init__(
        self,
        chunks: List[DocumentChunk],
    ) -> None:

        self.chunks = chunks

        tokenized_corpus = [
            chunk.text.lower().split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(
            tokenized_corpus
        )

        print("BM25 index built.")

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):

        tokenized_query = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked = sorted(
            zip(scores, self.chunks),
            reverse=True,
            key=lambda x: x[0],
        )

        return ranked[:top_k]