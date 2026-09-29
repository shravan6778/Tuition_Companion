class OpenAICompatProvider:
    """Works with Azure Foundry (v1 API), OpenAI, or any OpenAI-compatible endpoint."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout: int):
        from openai import OpenAI

        # max_retries=1: the SDK retries once with backoff on 429/5xx/timeouts (Rules.md).
        self._client = OpenAI(base_url=base_url or None, api_key=api_key, timeout=timeout, max_retries=1)
        self.model_name = model

    def complete_json(self, system: str, user: str) -> str:
        res = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        return res.choices[0].message.content or ""