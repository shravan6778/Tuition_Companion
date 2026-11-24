from app.core.config import settings

from .base import LLMProvider
from .fake_provider import FakeLLMProvider


def get_llm_provider() -> LLMProvider:
    provider = _build_llm_provider()
    if settings.usage_metering_enabled:  # kill switch + daily caps + usage_events (usage/)
        from app.usage.metered import MeteredLLM

        return MeteredLLM(provider, settings.llm_provider)
    return provider


def _build_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai_compat":
        if not settings.llm_api_key or not settings.llm_model:
            raise RuntimeError("LLM is not configured. Set LLM_API_KEY, LLM_MODEL (and LLM_BASE_URL for Azure).")
        from .openai_compat_provider import OpenAICompatProvider

        return OpenAICompatProvider(
            settings.llm_base_url, settings.llm_api_key, settings.llm_model, settings.llm_timeout_s
        )
    return FakeLLMProvider()


__all__ = ["LLMProvider", "get_llm_provider"]