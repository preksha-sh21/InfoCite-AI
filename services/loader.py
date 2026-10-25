"""
PDF loading service.
"""

from pathlib import Path
from typing import List, Union

import fitz

from core.config import (
    PDF_OCR_DPI,
    PDF_OCR_ENABLED,
    PDF_OCR_LANGUAGE,
    PDF_TABLE_EXTRACTION_ENABLED,
)


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
            text = page.get_text("text")
            if PDF_OCR_ENABLED and len(text.strip()) < 20:
                try:
                    text_page = page.get_textpage_ocr(
                        language=PDF_OCR_LANGUAGE,
                        dpi=PDF_OCR_DPI,
                        full=True,
                    )
                    text = page.get_text("text", textpage=text_page)
                except RuntimeError as exc:
                    raise RuntimeError(
                        "PDF OCR is enabled, but Tesseract OCR is unavailable. "
                        "Install Tesseract and its language data, or disable PDF_OCR_ENABLED."
                    ) from exc
            if PDF_TABLE_EXTRACTION_ENABLED:
                try:
                    tables = page.find_tables().tables
                    table_text = []
                    for table in tables:
                        markdown = table.to_markdown().strip()
                        if markdown:
                            table_text.append(markdown)
                    if table_text:
                        text = f"{text.rstrip()}\n\n" + "\n\n".join(
                            f"Extracted table {index}:\n{content}"
                            for index, content in enumerate(table_text, start=1)
                        )
                except Exception:
                    # Keep ordinary page text usable when table detection fails.
                    pass
            pages.append(text)

    return pages
