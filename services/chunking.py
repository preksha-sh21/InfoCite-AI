"""
Text preprocessing and chunking utilities.
"""

import re
import uuid
from typing import List

from core.config import CHUNK_OVERLAP, CHUNK_SIZE
from models.document_chunk import DocumentChunk


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """
    text = text.replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into overlapping chunks.
    """
    chunks: List[str] = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def build_document_chunks(
    pages: List[str],
    source: str,
) -> List[DocumentChunk]:
    """
    Convert PDF pages into DocumentChunk objects.
    """
    document_chunks: List[DocumentChunk] = []

    for page_number, page_text in enumerate(pages, start=1):
        cleaned = clean_text(page_text)
        page_chunks = chunk_text(cleaned)

        for chunk_index, chunk in enumerate(page_chunks):
            document_chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    text=chunk,
                    source=source,
                    page_number=page_number,
                    chunk_index=chunk_index,
                )
            )

    return document_chunks