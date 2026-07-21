"""
Simple script to verify the PDF loading and chunking pipeline.

Run using:
    python -m scripts.test_loader
"""

from app.chunking import build_document_chunks
from app.config import PDF_PATH
from app.loader import load_pdf


def main() -> None:
    pages = load_pdf(PDF_PATH)

    chunks = build_document_chunks(
        pages=pages,
        source=PDF_PATH.name,
    )

    print(f"Pages: {len(pages)}")
    print(f"Chunks: {len(chunks)}")

    print("-" * 60)

    first_chunk = chunks[0]

    print("Chunk ID:")
    print(first_chunk.chunk_id)

    print()

    print("Page:")
    print(first_chunk.page_number)

    print()

    print("Chunk Index:")
    print(first_chunk.chunk_index)

    print()

    print("Text Preview:\n")
    print(first_chunk.text[:500])


if __name__ == "__main__":
    main()