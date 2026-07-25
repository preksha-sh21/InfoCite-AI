from core.config import PDF_PATH

from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.bm25 import BM25Retriever


def main() -> None:

    pages = load_pdf(PDF_PATH)

    chunks = build_document_chunks(
        pages,
        PDF_PATH.name,
    )

    retriever = BM25Retriever(
        chunks
    )

    while True:

        query = input("\nQuestion: ")

        if query.lower() == "exit":
            break

        results = retriever.search(query)

        print()

        print("=" * 70)

        for rank, (score, chunk) in enumerate(
            results,
            start=1,
        ):

            print(f"Rank {rank}")

            print(f"BM25 Score: {score:.4f}")

            print(f"Page: {chunk.page_number}")

            print()

            print(chunk.text[:400])

            print()

            print("-" * 70)


if __name__ == "__main__":
    main()