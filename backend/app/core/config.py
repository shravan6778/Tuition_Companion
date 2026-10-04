from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    database_url: str
    supertokens_connection_uri: str = "http://localhost:3567"
    supertokens_api_key: str | None = None
    app_name: str = "Tuition Companion"
    api_domain: str = "http://localhost:8000"
    website_domain: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"
    storage_dir: str = "storage"
    max_upload_mb: int = 20
    chapter_processing_timeout_min: int = 15  # a 'processing' chapter older than this is treated as stuck
    ocr_provider: str = "fake"  # "fake" for local dev/tests, "azure" for Azure Document Intelligence
    azure_doc_intel_endpoint: str = ""
    azure_doc_intel_key: str = ""
    llm_provider: str = "fake"  # "fake" or "openai_compat" (Azure Foundry, OpenAI, etc.)
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"  # on Azure this is your DEPLOYMENT name
    llm_timeout_s: int = 60
    concept_max_chars: int = 12000  # per-page LLM input cap
    link_max_concepts: int = 120  # chapters with more concepts skip the LLM linking pass
    # --- page matching (pipeline/fingerprint.py, pipeline/matching.py)
    fingerprint_min_words: int = 15  # shorter pages (covers, blanks) are never fingerprinted or matched
    reuse_similarity: float = 0.95  # >= this: same page, reuse its concepts (no LLM call)
    variant_min_similarity: float = 0.60  # >= this (and < reuse): page of a variant/edition
    variant_min_coverage: float = 0.50  # share of a chapter's pages that must match one book to suggest it


settings = Settings()