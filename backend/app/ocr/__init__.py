from app.core.config import settings

from .base import OCRProvider, OCRResult
from .fake_provider import FakeOCRProvider


def get_ocr_provider() -> OCRProvider:
    provider = _build_ocr_provider()
    if settings.usage_metering_enabled:  # kill switch + daily caps + usage_events (usage/)
        from app.usage.metered import MeteredOCR

        return MeteredOCR(provider, "azure_doc_intel" if settings.ocr_provider == "azure" else settings.ocr_provider)
    return provider


def _build_ocr_provider() -> OCRProvider:
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