import io

import pypdf

from .base import OCRResult

_PLACEHOLDER = "[fake-ocr] No extractable text in this file. Set OCR_PROVIDER=azure for real OCR."


class FakeOCRProvider:
    """Local stand-in for Azure Document Intelligence, for development and tests
    without Azure credentials. Extracts real text from text-based PDFs; falls back
    to a placeholder for scanned PDFs or images, since this fake does no real OCR."""

    def extract(self, data: bytes, ext: str) -> OCRResult:
        if ext == "pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(data))
                text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
                if text:
                    return OCRResult(text=text, page_count=len(reader.pages))
            except Exception:
                pass  # not a real/parseable PDF (common for fake test fixtures) - fall through
        return OCRResult(text=_PLACEHOLDER, page_count=1)