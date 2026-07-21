"""
Central configuration for InfoCite AI.
"""

from pathlib import Path

# Project Paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

PDF_PATH = RAW_DATA_DIR / "cuda_programming_guide.pdf"

CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# Chunking

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# Embedding Model

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Retrieval

TOP_K = 5