import hashlib
import math

from app.core.config import FAKE_EMBEDDING_MODEL
from app.pipeline.fingerprint import tokenize


class FakeEmbeddingProvider:
    """Deterministic stand-in for tests and keyless local dev: words (and word pairs) are hashed into the
    vector, so texts that share words have a higher cosine similarity. Placeholder vectors, not real meaning:
    scripts refuse it unless --allow-fake, and a real run never reuses them (the model name differs)."""

    model_name = FAKE_EMBEDDING_MODEL

    def __init__(self, dim: int):
        self.dim = dim
        self.calls = 0  # how many embed() calls were made (tests assert on this)
        self.texts_embedded = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        self.texts_embedded += len(texts)
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        tokens = tokenize(text) or ["<empty>"]
        features = tokens + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dim
            vector[index] += 1.0 if digest[4] & 1 else -1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]
