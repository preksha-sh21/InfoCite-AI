from core.config import PDF_PATH

from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.bm25 import BM25Retriever
from services.hybrid_retriever import HybridRetriever


def main():

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

    while True:

        query = input("\nQuestion: ")

        if query.lower() == "exit":
            break

        results = hybrid.retrieve(query)

        print("\n")

        print("=" * 80)

        for i, result in enumerate(results, start=1):

            print(f"Rank {i}")

            print(f"RRF Score: {result['rrf_score']:.4f}")

            print(f"Page: {result['page']}")

            print()

            print(result["text"][:400])

            print()

            print("-" * 80)


if __name__ == "__main__":
    main()