"""
PDF loading service.
"""

from pathlib import Path
from typing import List, Union

import fitz


def load_pdf(pdf_path: Union[str, Path]) -> List[str]:
    """
    Load a PDF and return the extracted text for each page.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: List[str] = []

    with fitz.open(pdf_path) as document:
        for page in document:
            pages.append(page.get_text("text"))

    return pages