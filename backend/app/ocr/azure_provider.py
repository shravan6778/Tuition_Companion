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
    """Azure Document Intelligence using prebuilt-layout (text, layout, and page-by-page structure)."""

    def __init__(self, endpoint: str, key: str):
        self._endpoint = endpoint
        self._key = key

    def _analyze(self, data: bytes, ext: str):
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        client = DocumentIntelligenceClient(self._endpoint, AzureKeyCredential(self._key))
        poller = client.begin_analyze_document("prebuilt-layout", body=io.BytesIO(data))
        result = poller.result()
        analyzed = len(result.pages or [])

        # The free F0 tier silently returns only the first 2 pages. Never save a partial upload.
        expected = _pdf_page_count(data) if ext == "pdf" else None
        if expected and analyzed < expected:
            raise ProcessingError(
                f"Only {analyzed} of {expected} pages were read. The OCR resource may be on the "
                "free tier (2-page limit). Upgrade it to Standard (S0), then retry."
            )
        return result, analyzed

    def extract(self, data: bytes, ext: str) -> OCRResult:
        result, analyzed = self._analyze(data, ext)
        return OCRResult(text=result.content or "", page_count=analyzed)

    def extract_layout(self, data: bytes, ext: str) -> dict:
        result, analyzed = self._analyze(data, ext)

        pages_data = []
        for page in (result.pages or []):
            lines = getattr(page, "lines", []) or []
            page_text = " ".join([line.content for line in lines if getattr(line, "content", None)])
            pages_data.append({
                "page_number": getattr(page, "page_number", len(pages_data) + 1),
                "text": page_text,
                "lines": [
                    {
                        "content": getattr(line, "content", ""),
                        "polygon": getattr(line, "polygon", None),
                    }
                    for line in lines
                ],
            })

        paragraphs_data = []
        for p in (result.paragraphs or []):
            paragraphs_data.append({
                "role": getattr(p, "role", None),
                "content": getattr(p, "content", ""),
            })

        return {
            "text": result.content or "",
            "page_count": analyzed,
            "pages": pages_data,
            "paragraphs": paragraphs_data,
        }