"""PDF text extraction using PyMuPDF."""

from pathlib import Path

import fitz


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text content from a PDF file.

    Uses PyMuPDF to extract text from each page and concatenates
    them with page separators.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text content as a single string.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        RuntimeError: If the PDF cannot be read or parsed.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        doc: fitz.Document = fitz.open(str(pdf_path))
    except Exception as exc:
        raise RuntimeError(f"Failed to open PDF {pdf_path}: {exc}") from exc

    pages: list[str] = []
    for page_num in range(len(doc)):
        page: fitz.Page = doc[page_num]
        text: str = page.get_text("text")
        if text.strip():
            pages.append(text.strip())

    doc.close()

    full_text: str = "\n\n---\n\n".join(pages)

    if not full_text.strip():
        raise RuntimeError(
            f"No text extracted from {pdf_path}. "
            "The PDF may be image-based and require OCR."
        )

    return full_text
