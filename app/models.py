from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """
    Represents a single chunk of text extracted from a document.
    """

    chunk_id: str
    text: str
    source: str
    page_number: int
    chunk_index: int