from typing import Optional

from app.core.config import settings

from .base import EmbeddingError, EmbeddingProvider
from .fake_provider import FakeEmbeddingProvider


def get_embedding_provider() -> Optional[EmbeddingProvider]:
    """None means embeddings are switched off (EMBEDDING_PROVIDER=none): the pipeline skips them."""
    kind = settings.embedding_provider.lower()
    if kind == "openai_compat":
        api_key = settings.embedding_api_key or settings.llm_api_key  # same Azure resource by default
        base_url = settings.embedding_base_url or settings.llm_base_url
        if not api_key or not settings.embedding_model:
            raise RuntimeError(
                "Embeddings are not configured. Set EMBEDDING_MODEL (your Azure deployment name) and either "
                "EMBEDDING_API_KEY / EMBEDDING_BASE_URL or the LLM_* ones (used when the EMBEDDING_* ones are blank)."
            )
        from .openai_compat_provider import OpenAICompatEmbeddingProvider

        return OpenAICompatEmbeddingProvider(
            base_url, api_key, settings.embedding_model, settings.embedding_dim,
            batch_size=settings.embedding_batch_size, timeout_s=settings.embedding_timeout_s,
            send_dimensions=settings.embedding_send_dimensions,
        )
    if kind == "fake":
        return FakeEmbeddingProvider(settings.embedding_dim)
    return None


__all__ = ["EmbeddingError", "EmbeddingProvider", "get_embedding_provider"]
