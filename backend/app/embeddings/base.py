from typing import Protocol


class EmbeddingError(Exception):
    """An embedding call failed or returned something unusable. The message is for logs, not for users:
    embeddings are derived data, so nothing here is ever shown to a teacher or student."""


class EmbeddingProvider(Protocol):
    model_name: str  # recorded next to every vector; vectors of different models are never mixed
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """One vector per text, in the same order, each of length `dim`. Texts must be non-empty."""
        ...
