from core.config import PDF_PATH
from services.chunking import build_document_chunks
from services.loader import load_pdf
from services.embeddings import EmbeddingService


def main() -> None:
    print("1. Loading PDF...")
    pages = load_pdf(PDF_PATH)

    print("2. Building chunks...")
    chunks = build_document_chunks(
        pages=pages,
        source=PDF_PATH.name,
    )

    print(f"Built {len(chunks)} chunks")

    print("3. Loading embedding model...")
    embedding_service = EmbeddingService()

    first_chunk = chunks[0]

    print("4. Generating embedding...")
    embedding = embedding_service.generate_embedding(first_chunk.text)

    print("5. Embedding generated!")

    print("-" * 60)
    print(f"Chunk Length: {len(first_chunk.text)}")
    print(f"Embedding Dimension: {len(embedding)}")
    print("\nFirst 10 Values:\n")
    print(embedding[:10])


if __name__ == "__main__":
    main()