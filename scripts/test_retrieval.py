from core.config import TOP_K

from services.embeddings import EmbeddingService
from services.vector_store import VectorStore


def main() -> None:

    embedding_service = EmbeddingService()

    vector_store = VectorStore()

    query = input("Ask a question: ")

    print("\nGenerating query embedding...\n")

    query_embedding = embedding_service.generate_embedding(
        query
    )

    print("Searching ChromaDB...\n")

    results = vector_store.query(
        query_embedding=query_embedding,
        top_k=TOP_K,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("=" * 80)

    for i, (doc, meta, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):

        print(f"Result {i}")
        print(f"Page: {meta['page']}")
        print(f"Source: {meta['source']}")
        print(f"Distance: {distance:.4f}")

        print()

        print(doc[:500])

        print()

        print("-" * 80)


if __name__ == "__main__":
    main()