from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.bm25 import BM25Retriever
from services.hybrid_retriever import HybridRetriever
from services.reranker import CrossEncoderReranker
from services.llm import LLMService
from services.verifier import CitationVerifier
from core.config import (
    EMBEDDING_MODEL,
    LLM_MODEL,
)


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.
    """

    def __init__(self):

        print("Initializing InfoCite AI...")

        self.embedding_service = EmbeddingService()

        self.vector_store = VectorStore()

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

            print(f"Chunks created from {pdf_path.name}: {len(chunks)}")

            all_chunks.extend(chunks)

        print(f"Total chunks created: {len(all_chunks)}")
        self.index_stats = {
            "documents": len(pdf_paths),
            "chunks": len(all_chunks),
            "retriever": "Hybrid",
            "embeddings": EMBEDDING_MODEL,
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

    def ask(self, question: str):

        if self.hybrid is None:
            raise ValueError(
                "No documents have been indexed. Please upload and index PDFs first."
            )

        try:
            retrieved_chunks = self.hybrid.retrieve(
                query=question,
                top_k=10,
            )
        finally:
            self.embedding_service.unload_model()

        try:
            ranked_chunks = self.reranker.rerank(
                query=question,
                retrieved_chunks=retrieved_chunks,
            )
        finally:
            self.reranker.unload_model()

        print("\nTop ranked chunk:")
        print(ranked_chunks[0])

        answer = self.llm.generate_answer(
            query=question,
            chunks=ranked_chunks,
        )

        citations = self.verifier.extract_pages(
            ranked_chunks,
        )

        confidence = self.verifier.confidence(
            ranked_chunks,
        )

        evidence = self.verifier.extract_evidence(
          ranked_chunks,
        )

        return {
            "answer": answer,
            "sources": citations,
            "evidence": evidence,
            "confidence": confidence,
        }