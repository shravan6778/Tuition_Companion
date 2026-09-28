import hashlib
import os
from pathlib import Path

from app.core.config import settings

# Magic bytes -> extension. We trust file content, never the client's filename or MIME type.
_SIGNATURES = {
    b"%PDF-": "pdf",
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
}


def detect_extension(data: bytes) -> str | None:
    for magic, ext in _SIGNATURES.items():
        if data.startswith(magic):
            return ext
    return None


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save_by_hash(data: bytes, file_hash: str, ext: str) -> str:
    """Store content under its hash, so identical files are stored once.
    Returns the path relative to the storage root."""
    root = Path(settings.storage_dir)
    rel = Path(file_hash[:2]) / f"{file_hash}.{ext}"
    target = root / rel
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, target)  # atomic: never leaves a half-written file
    return rel.as_posix()