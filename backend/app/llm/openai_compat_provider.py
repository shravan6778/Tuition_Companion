import base64
import json
import logging

from openai import OpenAI

from app.core.config import settings
from app.core.errors import ProcessingError

logger = logging.getLogger(__name__)


class OpenAICompatProvider:
    """Any OpenAI-compatible endpoint: OpenAI, or Azure OpenAI / Foundry via its /openai/v1/ base URL.
    On Azure, `model` is your DEPLOYMENT name."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: int = 60):
        self.model_name = model
        self.vision_model = settings.vision_model or model
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

    def describe_figure(self, image_bytes: bytes, *, page_number: int, label: str | None = None) -> str:
        """Describe a textbook figure/graph without storing the image."""
        try:
            data_url = "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")
            prompt = (
                f"Describe the textbook figure on page {page_number}"
                + (f" ({label})" if label else "")
                + ". Explain visible axes and units, labels, trend/relationship, important points, and what the figure means "
                  "for a student. Do not invent values that are unreadable. Return JSON only as "
                  '{"description":"..."}'
            )
            resp = self._client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": "You are a careful educational vision parser. Describe only what is visible."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ]},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            obj = json.loads(raw)
            return str(obj.get("description") or "").strip()[:6000]
        except Exception as exc:
            logger.exception("Vision figure description failed")
            raise ProcessingError("The AI vision service couldn't describe a textbook figure.") from exc

