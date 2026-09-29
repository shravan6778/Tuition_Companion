import io

from app.core.errors import ProcessingError

from .base import OCRResult


def _pdf_page_count(data: bytes) -> int | None:
    try:
        import pypdf

        return len(pypdf.PdfReader(io.BytesIO(data)).pages)
    except Exception:
        return None


class AzureDocIntelProvider:
    """Azure Document Intelligence, prebuilt-read model (plain text + page count)."""

    def __init__(self, endpoint: str, key: str):
        self._endpoint = endpoint
        self._key = key

    def extract(self, data: bytes, ext: str) -> OCRResult:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        client = DocumentIntelligenceClient(self._endpoint, AzureKeyCredential(self._key))
        poller = client.begin_analyze_document("prebuilt-read", body=io.BytesIO(data))
        result = poller.result()
        analyzed = len(result.pages or [])

        # The free F0 tier silently returns only the first 2 pages. Never save a partial chapter.
        expected = _pdf_page_count(data) if ext == "pdf" else None
        if expected and analyzed < expected:
            raise ProcessingError(
                f"Only {analyzed} of {expected} pages were read. The OCR resource may be on the "
                "free tier (2-page limit). Upgrade it to Standard (S0), then retry."
            )
        return OCRResult(text=result.content or "", page_count=analyzed)