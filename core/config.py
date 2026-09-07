"""
Central configuration for InfoCite AI.
"""

import os
from pathlib import Path


# Project Paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

PDF_PATH = RAW_DATA_DIR / "cuda_programming_guide.pdf"

CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# Chunking Configuration

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Embedding Configuration

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

BATCH_SIZE = 32

# Retrieval Configuration

TOP_K = 5

# =============================================================================
# ChromaDB
# =============================================================================

CHROMA_COLLECTION_NAME = "infocite_documents"


RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

RERANK_TOP_K = 5

# Ollama is the default for local development. A hosted OpenAI-compatible
# provider can be selected for deployment through environment variables.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")

MAX_CONTEXT_CHUNKS = 5

TEMPERATURE = 0.2