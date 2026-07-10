"""PDF text extraction.

We extract the text layer with pypdf and convert that. PDFs are consumed as
input only; output is written as text/markdown (regenerating a laid-out PDF is
out of scope). Scanned PDFs with no text layer are not supported (no OCR).
"""

from __future__ import annotations

from pathlib import Path


def extract_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Reading PDFs needs the 'pypdf' package. Run: pip install pypdf"
        ) from exc

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n\n".join(pages).strip()
    if not text:
        raise RuntimeError(
            f"No extractable text found in {path.name}. If it is a scanned "
            "document, OCR it first (this tool does not do OCR)."
        )
    return text
