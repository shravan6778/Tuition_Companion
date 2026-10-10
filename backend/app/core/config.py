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
    ocr_provider: str = "azure"  # "fake" for local dev/tests, "azure" for Azure Document Intelligence
    azure_doc_intel_endpoint: str = ""
    azure_doc_intel_key: str = ""
    llm_provider: str = "openai_compat"  # "fake" or "openai_compat" (Azure Foundry, OpenAI, etc.)
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"  # on Azure this is your DEPLOYMENT name
    llm_timeout_s: int = 60
    concept_max_chars: int = 12000  # per-page LLM input cap
    concept_merge_similarity: float = 0.92  # name-embedding cosine at/above which two concepts in a chapter are one
    # --- cross-chapter prerequisites (pipeline/crosslink.py)
    crosslink_enabled: bool = True
    crosslink_candidates: int = 6  # nearest earlier concepts offered to the model per new concept
    crosslink_min_similarity: float = 0.40  # below this an earlier concept is never offered
    crosslink_keep_similarity: float = 0.50  # a link the model chose is dropped below this (counted as dropped_weak)
    crosslink_max_per_concept: int = 3
    crosslink_batch: int = 25  # new concepts per LLM call
    crosslink_max_concepts: int = 200  # a chapter with more new concepts is not cross-linked
    crosslink_max_relinks: int = 30  # later chapters re-linked when an earlier one changes
    link_max_concepts: int = 120  # chapters with more concepts skip the LLM linking pass
    # --- uploads & requests (content_library/upload.py, link_requests.py)
    require_front_pages: bool = False  # True: a Book can only be created from confirmed front-page metadata
    front_pages_max_pages: int = 8
    # Comma-separated usernames of teachers who may also delete OFFICIAL books and chapters from the UI/API (empty = nobody).
    # Everyone else can only delete their own books and chapters. Example: ADMIN_USERNAMES=sandy
    admin_usernames: str = ""
    max_whole_book_mb: int = 100
    max_whole_book_chapters: int = 60
    open_requests_per_student: int = 10
    # --- rate limits (per user, per process; see core/ratelimit.py)
    rate_join_per_min: int = 10  # student room join codes (brute-forceable in principle)
    rate_parent_link_per_min: int = 10  # parent->student link codes
    rate_front_pages_per_hour: int = 10  # each call costs one OCR + one LLM call
    rate_whole_book_plan_per_hour: int = 10
    # --- page matching (pipeline/fingerprint.py, pipeline/matching.py)
    fingerprint_min_words: int = 15  # shorter pages (covers, blanks) are never fingerprinted or matched
    reuse_similarity: float = 0.95  # >= this: same page, reuse its concepts (no LLM call)
    variant_min_similarity: float = 0.60  # >= this (and < reuse): page of a variant/edition
    variant_min_coverage: float = 0.50  # share of a chapter's pages that must match one book to suggest it
    # --- Layer 3: chapter-title sequence as a third signal (pipeline/structure.py)
    structure_enabled: bool = True
    structure_title_overlap: float = 0.75  # share of the shorter title's words that the other title contains
    structure_min_chapters: int = 2  # in-order matching chapters needed; one matching title proves nothing
    # --- Layer 4: embeddings as a second similarity signal (pipeline/embedmatch.py)
    embed_match_enabled: bool = True
    embed_match_similarity: float = 0.85  # page vs page cosine at or above this counts as the same content (a guess until `python -m app.db.embedmatch` shows real numbers)
    embed_match_max_pages: int = 20000  # more candidate page vectors than this: skip (keeps the in-memory compare small)
    # --- embeddings (embeddings/, pipeline/indexing.py). PostgreSQL holds the durable copy of every vector.
    embedding_provider: str = "none"  # "none" (skip) | "fake" (tests/dev) | "openai_compat" (OpenAI, Azure OpenAI/Foundry)
    embedding_base_url: str = ""  # blank -> llm_base_url (same Azure resource)
    embedding_api_key: str = ""  # blank -> llm_api_key
    embedding_model: str = "text-embedding-3-small"  # on Azure this is your DEPLOYMENT name
    embedding_dim: int = 1536  # text-embedding-3-small's native size; must match the Memgraph vector index
    embedding_batch_size: int = 32
    embedding_timeout_s: int = 60
    embedding_max_chars: int = 6000  # per-page input cap (keeps Hindi/Telugu pages under the model's token limit)
    embedding_send_dimensions: bool = False  # True: ask the API for `embedding_dim` (text-embedding-3 models only)
    # --- graph store (graph_store/). Memgraph is a rebuildable copy of what PostgreSQL holds.
    graph_store_provider: str = "none"  # "none" (skip) | "fake" (tests) | "memgraph"
    memgraph_uri: str = "bolt://localhost:7687"
    memgraph_user: str = ""
    memgraph_password: str = ""
    memgraph_vector_capacity: int = 20000  # initial vectors per index; Memgraph resizes beyond it
    memgraph_vector_metric: str = "cos"
    graph_sync_batch: int = 200  # rows per UNWIND statement when writing a chapter
    graph_search_max_candidates: int = 2000  # ceiling for the over-fetch that tenant filtering needs


settings = Settings()

FAKE_EMBEDDING_MODEL = "fake-embedding"


def refuse_fake_llm(allow_fake: bool) -> None:
    """Scripts that write public/permanent content must not run on the placeholder model by accident."""
    if settings.llm_provider.lower() == "fake" and not allow_fake:
        raise SystemExit(
            "LLM_PROVIDER is 'fake': it produces PLACEHOLDER concepts (snippets of page text chained together), "
            "not real extraction. Set LLM_PROVIDER=openai_compat plus LLM_BASE_URL / LLM_API_KEY / LLM_MODEL in "
            "backend/.env, or pass --allow-fake if you really want placeholders."
        )


def refuse_fake_embeddings(allow_fake: bool) -> None:
    """Scripts that fill the permanent vector copy must not run on hash-based placeholder vectors by accident."""
    if settings.embedding_provider.lower() == "fake" and not allow_fake:
        raise SystemExit(
            "EMBEDDING_PROVIDER is 'fake': it produces PLACEHOLDER vectors (hashed words), not real embeddings. "
            "Set EMBEDDING_PROVIDER=openai_compat plus EMBEDDING_MODEL (your Azure deployment name) in backend/.env, "
            "or pass --allow-fake if you really want placeholders."
        )
