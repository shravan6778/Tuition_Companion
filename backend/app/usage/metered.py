"""Wrappers that put the usage meter around the LLM, OCR, embedding and speech providers.

They are applied inside the provider factories (llm/, ocr/, embeddings/, speech/ `get_*_provider()`), so no call site
changes. A wrapper behaves like the provider it wraps (same methods and attributes); it adds, around each call:
the kill-switch / daily-cap check before, and one usage_events row after (real token or page counts when the provider
reports them, otherwise an estimate marked `estimated`)."""
import io
import logging
from typing import Any

from app.core.errors import QuotaExceededError
from app.embeddings.base import EmbeddingError
from app.speech.base import SpeechError
from app.usage import service

logger = logging.getLogger(__name__)


class QuotaExceededEmbeddingError(QuotaExceededError, EmbeddingError):
    """Embeddings are derived data: callers already treat EmbeddingError as 'try again later', never as a failure."""


class QuotaExceededSpeechError(QuotaExceededError, SpeechError):
    pass


def _reported(inner: Any) -> int | None:
    value = getattr(inner, "last_total_tokens", None)
    return int(value) if isinstance(value, int) and value > 0 else None


class _Metered:
    quota = ""
    provider_name = ""
    error_cls: type[QuotaExceededError] = QuotaExceededError

    def __init__(self, inner: Any, provider_name: str):
        self._inner = inner
        self.provider_name = provider_name

    def __getattr__(self, name: str):  # model_name, dim, vision_model, ... come from the wrapped provider
        return getattr(self._inner, name)

    def _guard(self, operation: str, needed: int = 0) -> None:
        service.check_allowed(self.quota, provider=self.provider_name, operation=operation, needed=needed, error_cls=self.error_cls)

    def _record(self, operation: str, units: int, *, status: str = "ok", estimated: bool = False) -> None:
        service.record(quota=self.quota, provider=self.provider_name, operation=operation, units=units, status=status, estimated=estimated)


class MeteredLLM(_Metered):
    quota = "llm_tokens"

    def complete_json(self, system: str, user: str) -> str:
        op = "llm.complete_json"
        self._guard(op, needed=service.estimate_tokens(system, user))
        self._inner.last_total_tokens = None
        try:
            out = self._inner.complete_json(system, user)
        except Exception:
            self._record(op, 0, status="error")
            raise
        tokens = _reported(self._inner)
        self._record(op, tokens or service.estimate_tokens(system, user, out), estimated=tokens is None)
        return out

    def __getattr__(self, name: str):
        attr = getattr(self._inner, name)
        if name != "describe_figure":
            return attr

        def describe_figure(image_bytes: bytes, **kwargs):  # a vision call: one image costs roughly 1,500 tokens
            op = "llm.describe_figure"
            self._guard(op, needed=1500)
            self._inner.last_total_tokens = None
            try:
                out = attr(image_bytes, **kwargs)
            except Exception:
                self._record(op, 0, status="error")
                raise
            tokens = _reported(self._inner)
            self._record(op, tokens or 1500 + service.estimate_tokens(out), estimated=tokens is None)
            return out

        return describe_figure


class MeteredEmbeddings(_Metered):
    quota = "embedding_tokens"
    error_cls = QuotaExceededEmbeddingError

    def embed(self, texts: list[str]) -> list[list[float]]:
        op = "embedding.embed"
        self._guard(op, needed=service.estimate_tokens(*texts))
        self._inner.last_total_tokens = None
        try:
            out = self._inner.embed(texts)
        except Exception:
            self._record(op, 0, status="error")
            raise
        tokens = _reported(self._inner)
        self._record(op, tokens or service.estimate_tokens(*texts), estimated=tokens is None)
        return out


def _pdf_pages(data: bytes, ext: str) -> int:
    if ext.lower() != "pdf":
        return 1
    try:
        import pypdf
        return max(1, len(pypdf.PdfReader(io.BytesIO(data)).pages))
    except Exception:
        return 1


class MeteredOCR(_Metered):
    quota = "ocr_pages"

    def extract(self, data: bytes, ext: str):
        op = "ocr.extract"
        self._guard(op, needed=_pdf_pages(data, ext))
        try:
            result = self._inner.extract(data, ext)
        except Exception:
            self._record(op, 0, status="error")
            raise
        self._record(op, int(getattr(result, "page_count", 0) or 1))
        return result

    def extract_layout(self, data: bytes, ext: str) -> dict:
        op = "ocr.extract_layout"
        self._guard(op, needed=_pdf_pages(data, ext))
        try:
            result = self._inner.extract_layout(data, ext)
        except Exception:
            self._record(op, 0, status="error")
            raise
        self._record(op, int(result.get("page_count") or 1))
        return result


class MeteredSpeech(_Metered):
    quota = "speech_calls"
    error_cls = QuotaExceededSpeechError

    def transcribe(self, audio: bytes, content_type: str, language: str):
        op = "speech.transcribe"
        self._guard(op, needed=1)
        try:
            out = self._inner.transcribe(audio, content_type, language)
        except Exception:
            self._record(op, 0, status="error")
            raise
        self._record(op, 1)
        return out
