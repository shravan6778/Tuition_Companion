"""Page fingerprints: 3-word-shingle MinHash + LSH band keys.

Why shingles of 3 words: a bag of single words says two pages are identical if they use the same words
in any order; 3-word shingles only match when the actual phrasing matches. Normalization is Unicode-aware
(the old ASCII-only version turned Hindi/Telugu pages into empty text)."""
import hashlib
import re
import unicodedata
from typing import Optional

import numpy as np
from datasketch import MinHash

from app.core.config import settings

NUM_PERM = 128
SHINGLE_SIZE = 3
BANDS = 32  # 32 bands x 4 rows: ~99% recall at Jaccard 0.6, ~5% false candidates at 0.2
ROWS = NUM_PERM // BANDS


def tokenize(text: str) -> list[str]:
    s = unicodedata.normalize("NFKC", text or "").casefold()
    return re.sub(r"[^\w\s]|_", " ", s).split()


def compute_minhash(text: str, min_words: Optional[int] = None) -> Optional[bytes]:
    """512-byte signature, or None when the page is too short to match reliably (covers, blanks)."""
    tokens = tokenize(text)
    if len(tokens) < max(min_words if min_words is not None else settings.fingerprint_min_words, SHINGLE_SIZE):
        return None
    m = MinHash(num_perm=NUM_PERM, seed=1)
    for i in range(len(tokens) - SHINGLE_SIZE + 1):
        m.update(" ".join(tokens[i:i + SHINGLE_SIZE]).encode("utf8"))
    return np.asarray(m.hashvalues, dtype=">u4").tobytes()


def compute_jaccard_similarity(sig_a: Optional[bytes], sig_b: Optional[bytes]) -> float:
    """Estimated Jaccard similarity of the two pages' shingle sets (0.0 if either has no signature)."""
    if not sig_a or not sig_b or len(sig_a) != len(sig_b):
        return 0.0
    a, b = np.frombuffer(sig_a, dtype=">u4"), np.frombuffer(sig_b, dtype=">u4")
    return float(np.mean(a == b))


def band_keys(signature: bytes) -> list[int]:
    """One 63-bit key per band; two pages sharing any key become match candidates."""
    values = np.frombuffer(signature, dtype=">u4")
    keys = []
    for band in range(BANDS):
        chunk = bytes([band]) + values[band * ROWS:(band + 1) * ROWS].tobytes()
        keys.append(int.from_bytes(hashlib.blake2b(chunk, digest_size=8).digest(), "big") & 0x7FFFFFFFFFFFFFFF)
    return keys


def apply_fingerprint(page, text: str) -> Optional[bytes]:
    """Sets the page's signature and LSH index rows (no-op for too-short pages)."""
    from app.models.content import PageBand  # local import: models import nothing from pipeline

    signature = compute_minhash(text)
    page.fingerprint = signature
    page.bands = [PageBand(key=k) for k in band_keys(signature)] if signature else []
    return signature
