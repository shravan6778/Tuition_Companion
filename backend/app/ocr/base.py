from dataclasses import dataclass
from typing import Protocol


@dataclass
class OCRResult:
    text: str
    page_count: int


class OCRProvider(Protocol):
    def extract(self, data: bytes, ext: str) -> OCRResult: ...
    def extract_layout(self, data: bytes, ext: str) -> dict:
        """Page-by-page result:
        {"text": str, "page_count": int,
         "pages": [{"page_number": int, "text": str, "lines": [...]}],
         "paragraphs": [{"role": str | None, "content": str}]}"""
        ...
