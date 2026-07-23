"""
Vector database service using ChromaDB.
"""

from typing import List

import chromadb
from chromadb.api.models.Collection import Collection

from core.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_DIR,
)
from models.document_chunk import DocumentChunk


class VectorStore:
    """
    Handles all interactions with ChromaDB.
    """

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR)
        )

        self.collection: Collection = (
            self.client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME
            )
        )

        print("ChromaDB initialized.")

    def count(self) -> int:
        """
        Return the number of stored vectors.
        """
        return self.collection.count()

    def reset(self) -> None:
        """
        Delete the existing collection and recreate it.
        """
        try:
            self.client.delete_collection(
                CHROMA_COLLECTION_NAME
            )
            print("Existing collection deleted.")

        except Exception:
            print("No existing collection found.")

        self.collection = (
            self.client.get_or_create_collection(
                name=CHROMA_COLLECTION_NAME
            )
        )

        print("Fresh collection created.")

    def add_documents(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> None:
        """
        Store document chunks and embeddings.
        """

        ids = [
            chunk.chunk_id
            for chunk in chunks
        ]

        documents = [
            chunk.text
            for chunk in chunks
        ]

        metadatas = [
            {
                "source": chunk.source,
                "page": chunk.page_number,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        print(f"Stored {len(chunks)} chunks in ChromaDB.")

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ):
        """
        Retrieve the most similar document chunks.
        """

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        return results