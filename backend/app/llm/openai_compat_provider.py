import logging

from openai import OpenAI

from app.core.errors import ProcessingError

logger = logging.getLogger(__name__)


class OpenAICompatProvider:
    """Any OpenAI-compatible endpoint: OpenAI, or Azure OpenAI / Foundry via its /openai/v1/ base URL.
    On Azure, `model` is your DEPLOYMENT name."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: int = 60):
        self.model_name = model
        self._client = OpenAI(base_url=base_url or None, api_key=api_key, timeout=timeout_s, max_retries=1)

    def complete_json(self, system: str, user: str) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # network, auth, quota, timeout
            logger.exception("LLM call failed")
            raise ProcessingError("The AI service couldn't be reached. Please try again in a moment.") from exc
        return resp.choices[0].message.content or ""
