from app.core.config import settings

from .base import OCRProvider, OCRResult
from .fake_provider import FakeOCRProvider


def get_ocr_provider() -> OCRProvider:
    if settings.ocr_provider == "azure":
        if not settings.azure_doc_intel_endpoint or not settings.azure_doc_intel_key:
            raise RuntimeError(
                "Azure Document Intelligence is not configured. Set AZURE_DOC_INTEL_ENDPOINT and "
                "AZURE_DOC_INTEL_KEY, or set OCR_PROVIDER=fake for local development."
            )
        from .azure_provider import AzureDocIntelProvider

        return AzureDocIntelProvider(settings.azure_doc_intel_endpoint, settings.azure_doc_intel_key)
    return FakeOCRProvider()


__all__ = ["OCRProvider", "OCRResult", "get_ocr_provider"]