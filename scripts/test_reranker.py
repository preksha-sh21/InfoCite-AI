from core.config import PDF_PATH

from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.bm25 import BM25Retriever
from services.hybrid_retriever import HybridRetriever
from services.reranker import CrossEncoderReranker


def main() -> None:

    print("Loading document...")

    pages = load_pdf(PDF_PATH)

    chunks = build_document_chunks(
        pages,
        PDF_PATH.name,
    )

    embedding_service = EmbeddingService()

    vector_store = VectorStore()

    bm25 = BM25Retriever(chunks)

    hybrid = HybridRetriever(
        vector_store,
        bm25,
        embedding_service,
    )

    reranker = CrossEncoderReranker()

    while True:

        query = input("\nQuestion: ")

        if query.lower() == "exit":
            break

        print("\nHybrid retrieval...")

        retrieved_chunks = hybrid.retrieve(
            query=query,
            top_k=10,
        )

        print("Cross-encoder reranking...\n")

        ranked_chunks = reranker.rerank(
            query=query,
            retrieved_chunks=retrieved_chunks,
        )

        print("=" * 80)

        for rank, chunk in enumerate(ranked_chunks, start=1):

            print(f"Rank {rank}")
            print(f"Cross Score : {chunk['cross_score']:.4f}")
            print(f"RRF Score   : {chunk['rrf_score']:.4f}")
            print(f"Page        : {chunk['page']}")

            print()

            print(chunk["text"][:500])

            print()

            print("-" * 80)


if __name__ == "__main__":
    main()