from .base import OCRResult

# Uses the "prebuilt-read" model, which returns plain text and page count without
# needing a custom-trained model. Import is lazy so the fake provider works even
# when the azure-ai-documentintelligence package isn't installed.


class AzureDocIntelProvider:
    def __init__(self, endpoint: str, key: str):
        self._endpoint = endpoint
        self._key = key

    def extract(self, data: bytes, ext: str) -> OCRResult:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        client = DocumentIntelligenceClient(self._endpoint, AzureKeyCredential(self._key))
        poller = client.begin_analyze_document(
            "prebuilt-read", body=data, content_type="application/octet-stream"
        )
        result = poller.result()
        return OCRResult(text=result.content or "", page_count=len(result.pages or []))