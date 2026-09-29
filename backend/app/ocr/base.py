from dataclasses import dataclass
from typing import Protocol


@dataclass
class OCRResult:
    text: str
    page_count: int


class OCRProvider(Protocol):
    def extract(self, data: bytes, ext: str) -> OCRResult: ...