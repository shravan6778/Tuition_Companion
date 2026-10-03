import io

import pypdf

from .base import OCRResult

_PLACEHOLDER = "[fake-ocr] No extractable text in this file. Set OCR_PROVIDER=azure for real OCR."


class FakeOCRProvider:
    """Local stand-in for Azure Document Intelligence, for development and tests
    without Azure credentials. Extracts real text from text-based PDFs; falls back
    to a placeholder for scanned PDFs or images, since this fake does no real OCR."""

    def _pages(self, data: bytes, ext: str) -> list[str]:
        if ext == "pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(data))
                pages = [(p.extract_text() or "").strip() for p in reader.pages]
                if any(pages):
                    return pages
            except Exception:
                pass  # not a real/parseable PDF (common for test fixtures) - fall through
        return [_PLACEHOLDER]

    def extract(self, data: bytes, ext: str) -> OCRResult:
        pages = self._pages(data, ext)
        return OCRResult(text="\n".join(pages), page_count=len(pages))

    def extract_layout(self, data: bytes, ext: str) -> dict:
        pages = self._pages(data, ext)
        return {
            "text": "\n".join(pages),
            "page_count": len(pages),
            "pages": [{"page_number": i + 1, "text": t, "lines": []} for i, t in enumerate(pages)],
            "paragraphs": [],
        }
