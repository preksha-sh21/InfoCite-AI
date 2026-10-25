from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.bm25 import BM25Retriever
from services.hybrid_retriever import HybridRetriever
from services.reranker import CrossEncoderReranker
from services.llm import LLMService
from services.verifier import CitationVerifier
from typing import Optional
from core.config import (
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    LLM_MODEL,
    NO_ANSWER_RERANKER_THRESHOLD,
    RERANKER_MODEL,
)


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.
    """

    def __init__(self, collection_name: str = CHROMA_COLLECTION_NAME):

        print("Initializing InfoCite AI...")

        self.embedding_service = EmbeddingService()

        self.vector_store = VectorStore(collection_name=collection_name)

        self.bm25 = None
        self.hybrid = None

        self.reranker = CrossEncoderReranker()

        self.llm = LLMService()

        self.verifier = CitationVerifier()
        self.index_stats = {
            "documents": 0,
            "chunks": 0,
            "retriever": "Hybrid",
            "embeddings": EMBEDDING_MODEL,
            "reranker": RERANKER_MODEL,
            "llm": LLM_MODEL,
        }

        print("InfoCite AI initialized successfully.")

    def index_documents(self, pdf_paths):
        """
        Load and index one or more PDF documents.
        """

        all_chunks = []

        for pdf_path in pdf_paths:
            print(f"Loading {pdf_path.name}...")

            pages = load_pdf(pdf_path)

            print(f"Pages extracted from {pdf_path.name}: {len(pages)}")

            for page_number, page_text in enumerate(pages, start=1):
                print(
                    f"    Page {page_number}: {len(page_text.strip())} characters"
                )

            chunks = build_document_chunks(
                pages,
                pdf_path.name,
            )

            if not chunks:
                raise ValueError(
                    f"No extractable text found in {pdf_path.name}. "
                    "Scanned PDFs need OCR before they can be indexed."
                )

            print(f"Chunks created from {pdf_path.name}: {len(chunks)}")

            all_chunks.extend(chunks)

        print(f"Total chunks created: {len(all_chunks)}")
        if not all_chunks:
            raise ValueError("No extractable text found in the uploaded PDFs.")
        self.index_stats = {
            "documents": len(pdf_paths),
            "chunks": len(all_chunks),
            "retriever": "Hybrid",
            "embeddings": EMBEDDING_MODEL,
            "reranker": RERANKER_MODEL,
            "llm": LLM_MODEL,
        }

        # Generate embeddings only while indexing, then release the model.
        texts = [
            chunk.text
            for chunk in all_chunks
        ]

        embeddings = None
        try:
            embeddings = self.embedding_service.generate_embeddings(
                texts
            )

            # Reset vector database
            self.vector_store.reset()

            # Store vectors
            self.vector_store.add_documents(
                all_chunks,
                embeddings,
            )
        finally:
            embeddings = None
            self.embedding_service.unload_model()

        # Build BM25 index
        self.bm25 = BM25Retriever(all_chunks)

        # Build Hybrid Retriever
        self.hybrid = HybridRetriever(
            self.vector_store,
            self.bm25,
            self.embedding_service,
        )

        print(
            f"Successfully indexed {len(pdf_paths)} document(s)."
        )

    def restore_documents(self, pdf_paths):
        """Rebuild the in-memory keyword index from a workspace's saved PDFs."""
        chunks = []
        for pdf_path in pdf_paths:
            pages = load_pdf(pdf_path)
            chunks.extend(build_document_chunks(pages, pdf_path.name))

        if not chunks or self.vector_store.count() == 0:
            self.index_documents(pdf_paths)
            return

        self.bm25 = BM25Retriever(chunks)
        self.hybrid = HybridRetriever(
            self.vector_store,
            self.bm25,
            self.embedding_service,
        )
        self.index_stats = {
            "documents": len(pdf_paths),
            "chunks": len(chunks),
            "retriever": "Hybrid",
            "embeddings": EMBEDDING_MODEL,
            "reranker": RERANKER_MODEL,
            "llm": LLM_MODEL,
        }

    def ask(self, question: str, history: Optional[list[dict]] = None):

        if not question or not question.strip():
            raise ValueError("Please enter a question.")

        if self.hybrid is None:
            raise ValueError(
                "No documents have been indexed. Please upload and index PDFs first."
            )

        recent_history = (history or [])[-3:]
        retrieval_query = question
        if recent_history:
            history_text = "\n".join(
                f"Q: {turn.get('question', '')} A: {turn.get('answer', '')[:400]}"
                for turn in recent_history
            )
            retrieval_query = f"Current question: {question}\nRecent context: {history_text}"

        try:
            retrieved_chunks = self.hybrid.retrieve(
                query=retrieval_query,
                top_k=10,
            )
        finally:
            self.embedding_service.unload_model()

        ranked_chunks = self.reranker.rerank(
            query=retrieval_query,
            retrieved_chunks=retrieved_chunks,
            evidence_query=question,
        )

        if (
            not ranked_chunks
            or ranked_chunks[0].get("reranker_score", float("-inf"))
            < NO_ANSWER_RERANKER_THRESHOLD
        ):
            return {
                "answer": "I don't have enough information in the provided documents.",
                "sources": [],
                "evidence": [],
                "evidence_match": "Low",
            }

        self.verifier.assign_citation_ids(ranked_chunks)

        answer = self.llm.generate_answer(
            query=question,
            chunks=ranked_chunks,
            history=recent_history,
        )

        citations = self.verifier.extract_pages(
            ranked_chunks,
        )

        evidence_match = self.verifier.evidence_match(
            ranked_chunks,
        )

        evidence = self.verifier.extract_evidence(
          ranked_chunks,
        )

        return {
            "answer": answer,
            "sources": citations,
            "evidence": evidence,
            "evidence_match": evidence_match,
        }
