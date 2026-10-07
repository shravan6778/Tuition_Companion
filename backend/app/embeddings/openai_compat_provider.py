import logging

from openai import OpenAI

from app.embeddings.base import EmbeddingError

logger = logging.getLogger(__name__)


class OpenAICompatEmbeddingProvider:
    """Any OpenAI-compatible embeddings endpoint: OpenAI, or Azure OpenAI / Foundry via its /openai/v1/ base URL.
    On Azure, `model` is your embedding DEPLOYMENT name (e.g. one that serves text-embedding-3-small)."""

    def __init__(self, base_url: str, api_key: str, model: str, dim: int, *, batch_size: int = 32,
                 timeout_s: int = 60, send_dimensions: bool = False, client=None):
        self.model_name = model
        self.dim = dim
        self._batch_size = max(1, batch_size)
        self._send_dimensions = send_dimensions
        self._client = client or OpenAI(base_url=base_url or None, api_key=api_key, timeout=timeout_s, max_retries=2)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start:start + self._batch_size]
            extra = {"dimensions": self.dim} if self._send_dimensions else {}
            try:
                response = self._client.embeddings.create(model=self.model_name, input=batch, **extra)
            except Exception as exc:  # network, auth, quota, unknown deployment
                logger.exception("Embedding call failed")
                raise EmbeddingError("The embedding service couldn't be reached.") from exc
            items = sorted(response.data, key=lambda item: item.index)
            if len(items) != len(batch):
                raise EmbeddingError(f"Asked for {len(batch)} embeddings, got {len(items)}.")
            for item in items:
                if len(item.embedding) != self.dim:
                    raise EmbeddingError(
                        f"The model returned {len(item.embedding)}-number vectors but EMBEDDING_DIM is {self.dim}. "
                        "Set EMBEDDING_DIM to the model's size (1536 for text-embedding-3-small)."
                    )
                vectors.append(list(item.embedding))
        return vectors
