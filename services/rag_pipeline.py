from services.loader import load_pdf
from services.chunking import build_document_chunks
from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.bm25 import BM25Retriever
from services.hybrid_retriever import HybridRetriever
from services.reranker import CrossEncoderReranker
from services.llm import LLMService
from services.verifier import CitationVerifier


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

        print("InfoCite AI initialized successfully.")

    def index_documents(self, pdf_paths):
        """
        Load and index one or more PDF documents.
        """

        all_chunks = []

        for pdf_path in pdf_paths:
            print(f"Loading {pdf_path.name}...")

            pages = load_pdf(pdf_path)

            chunks = build_document_chunks(
                pages,
                pdf_path.name,
            )

            all_chunks.extend(chunks)

        print(f"Total chunks created: {len(all_chunks)}")

        # Generate embeddings
        texts = [
            chunk.text
            for chunk in all_chunks
        ]

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

        retrieved_chunks = self.hybrid.retrieve(
            query=question,
            top_k=10,
        )

        ranked_chunks = self.reranker.rerank(
            query=question,
            retrieved_chunks=retrieved_chunks,
        )

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

        return {
            "answer": answer,
            "sources": citations,
            "confidence": confidence,
            "chunks": ranked_chunks,
        }