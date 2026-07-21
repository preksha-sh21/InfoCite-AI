from pathlib import Path
from typing import List, Union

import fitz


def load_pdf(pdf_path: Union[str, Path]) -> List[str]:
    """
    Load a PDF and return the extracted text for each page.

    Args:
        pdf_path: Path to the PDF document.

    Returns:
        A list where each element contains the text from one page.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: List[str] = []

    with fitz.open(pdf_path) as document:
        for page in document:
            pages.append(page.get_text("text"))

    return pages