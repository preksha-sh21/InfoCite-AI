from core.config import PDF_PATH

from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore


def main() -> None:

    print("1. Loading PDF...")
    pages = load_pdf(PDF_PATH)

    print("2. Chunking document...")
    chunks = build_document_chunks(
        pages=pages,
        source=PDF_PATH.name,
    )

    print(f"Built {len(chunks)} chunks.")

    print("3. Generating embeddings...")
    embedding_service = EmbeddingService()

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = embedding_service.generate_embeddings(
        texts
    )

    print("4. Initializing ChromaDB...")
    vector_store = VectorStore()

    if vector_store.count() > 0:
        print("Existing vectors detected.")
        print("Resetting collection...")
        vector_store.reset()

    print("5. Saving embeddings...")
    vector_store.add_documents(
        chunks,
        embeddings,
    )

    print()
    print("=" * 60)
    print("Vector database successfully built!")
    print(f"Stored vectors: {vector_store.count()}")
    print("=" * 60)


if __name__ == "__main__":
    main()