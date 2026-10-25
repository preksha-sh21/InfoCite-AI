"""Compare hybrid retrieval rankings before and after cross-encoder reranking."""

import argparse
import json
import time
import uuid
from pathlib import Path

from core.config import CHROMA_DB_DIR, NO_ANSWER_RERANKER_THRESHOLD, PDF_PATH
from services.bm25 import BM25Retriever
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.hybrid_retriever import HybridRetriever
from services.loader import load_pdf
from services.reranker import CrossEncoderReranker
from services.vector_store import VectorStore


def metrics(rows, key, cutoff):
    hit_rate = []
    reciprocal_rank = []
    recall = []

    for row in rows:
        relevant = set(row["expected_pages"])
        ranked_pages = row[key][:cutoff]
        first_rank = next(
            (rank for rank, page in enumerate(ranked_pages, start=1) if page in relevant),
            None,
        )
        hit_rate.append(1.0 if first_rank else 0.0)
        reciprocal_rank.append(1.0 / first_rank if first_rank else 0.0)
        recall.append(len(set(ranked_pages) & relevant) / len(relevant))

    count = max(len(rows), 1)
    return {
        f"hit_rate@{cutoff}": round(sum(hit_rate) / count, 3),
        f"mrr@{cutoff}": round(sum(reciprocal_rank) / count, 3),
        f"page_recall@{cutoff}": round(sum(recall) / count, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=PDF_PATH)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "evals" / "cuda_questions.json",
    )
    parser.add_argument("--cutoff", type=int, default=5)
    args = parser.parse_args()

    examples = json.loads(args.dataset.read_text(encoding="utf-8"))
    pages = load_pdf(args.pdf)
    chunks = build_document_chunks(pages, args.pdf.name)
    embedding_service = EmbeddingService()
    vector_store = None
    collection_name = f"eval_{uuid.uuid4().hex[:24]}"
    reranker = CrossEncoderReranker()
    rows = []

    try:
        vector_store = VectorStore(
            collection_name=collection_name,
            db_path=CHROMA_DB_DIR / "evaluation",
        )
        embeddings = embedding_service.generate_embeddings([chunk.text for chunk in chunks])
        vector_store.add_documents(chunks, embeddings)
        embedding_service.unload_model()
        hybrid = HybridRetriever(
            vector_store,
            BM25Retriever(chunks),
            embedding_service,
        )

        for example in examples:
            started = time.perf_counter()
            candidates = hybrid.retrieve(example["question"], top_k=20)
            retrieval_ms = (time.perf_counter() - started) * 1000
            baseline_pages = [item["page"] for item in candidates]

            started = time.perf_counter()
            reranked = reranker.rerank(example["question"], candidates)
            rerank_ms = (time.perf_counter() - started) * 1000
            rows.append({
                **example,
                "hybrid_pages": baseline_pages,
                "reranked_pages": [item["page"] for item in reranked],
                "top_reranker_score": reranked[0]["reranker_score"] if reranked else None,
                "abstained": not reranked or reranked[0]["reranker_score"] < NO_ANSWER_RERANKER_THRESHOLD,
                "retrieval_ms": retrieval_ms,
                "rerank_ms": rerank_ms,
            })
    finally:
        embedding_service.unload_model()
        reranker.unload_model()
        if vector_store is not None:
            vector_store.delete_collection()

    answerable_rows = [row for row in rows if row.get("answerable", True)]
    unanswerable_rows = [row for row in rows if not row.get("answerable", True)]
    print(json.dumps({
        "pdf": args.pdf.name,
        "queries": len(rows),
        "cutoff": args.cutoff,
        "abstention_threshold": NO_ANSWER_RERANKER_THRESHOLD,
        "answerable_queries": len(answerable_rows),
        "unanswerable_queries": len(unanswerable_rows),
        "hybrid": metrics(answerable_rows, "hybrid_pages", args.cutoff),
        "hybrid_plus_cross_encoder": metrics(answerable_rows, "reranked_pages", args.cutoff),
        "answerable_abstention_rate": round(
            sum(row["abstained"] for row in answerable_rows) / max(len(answerable_rows), 1), 3
        ),
        "unanswerable_false_answer_rate": round(
            sum(not row["abstained"] for row in unanswerable_rows) / max(len(unanswerable_rows), 1), 3
        ),
        "mean_retrieval_ms": round(sum(row["retrieval_ms"] for row in rows) / max(len(rows), 1), 1),
        "mean_rerank_ms": round(sum(row["rerank_ms"] for row in rows) / max(len(rows), 1), 1),
        "per_query": rows,
    }, indent=2))


if __name__ == "__main__":
    main()
