"""Vector storage helpers. PostgreSQL keeps each vector as raw float32 bytes (no pgvector extension needed:
similarity search happens in Memgraph; PostgreSQL is only the durable copy)."""
import numpy as np


def to_bytes(vector) -> bytes:
    return np.asarray(vector, dtype="<f4").tobytes()


def from_bytes(data: bytes) -> list[float]:
    return np.frombuffer(data, dtype="<f4").astype(float).tolist()


def cosine(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator else 0.0
