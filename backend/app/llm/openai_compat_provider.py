import json
import logging
from typing import Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL if hasattr(settings, "OPENAI_BASE_URL") else None,
        )
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    async def extract_concepts(self, page_text: str) -> list[dict[str, Any]]:
        """
        Extracts key concepts, descriptions, and learning objectives from a single page.
        Returns valid structured JSON.
        """
        if not page_text.strip():
            return []

        prompt = f"""You are an educational curriculum parser. Analyze the following textbook page content and extract:
1. Core concepts introduced or covered.
2. Short description of each concept.
3. Specific learning objectives.
4. Immediate prerequisite concepts if mentioned or implied.

Respond strictly in JSON format as a list of objects with keys:
"name", "description", "learning_objectives" (list of strings), "prerequisites" (list of strings).

Page Content:
\"\"\"{page_text}\"\"\"
"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise educational content extractor that only outputs JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            parsed = json.loads(raw)
            # Normalize if wrapped in a top-level key like {"concepts": [...]}
            if isinstance(parsed, dict):
                for val in parsed.values():
                    if isinstance(val, list):
                        return val
                return [parsed]
            return parsed if isinstance(parsed, list) else []
        except Exception as e:
            logger.error(f"Failed to extract concepts via LLM: {e}")
            return []