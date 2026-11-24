"""Refuse to run a public (non-dev) server with an unsafe configuration. Called once from main.py.

In ENV=dev the same problems are only logged as warnings, so local work is not blocked."""
import logging
from urllib.parse import urlparse

from app.core.config import Settings, settings as default_settings

logger = logging.getLogger(__name__)

# The password that used to be written into docker-compose.yml and .env.example in this repository's history.
# Anyone who ever saw the repo knows it, so no real deployment may use it.
LEAKED_PASSWORDS = ("Postgre21",)


def check_config(cfg: Settings | None = None) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings). Errors are only fatal outside ENV=dev."""
    cfg = cfg or default_settings
    errors: list[str] = []
    warnings: list[str] = []

    if not cfg.supertokens_api_key:
        errors.append("SUPERTOKENS_API_KEY is empty. Set it here AND as API_KEYS on the SuperTokens core, so only this API can talk to it.")
    try:
        password = urlparse(cfg.database_url).password or ""
    except ValueError:
        password = ""
    if cfg.database_url.startswith("postgres") and not password:
        errors.append("DATABASE_URL has no password.")
    if password in LEAKED_PASSWORDS:
        errors.append("DATABASE_URL uses the old password that was committed to the repository. Choose a new one (and rotate the database's).")
    if cfg.llm_provider.lower() != "fake" and not cfg.llm_no_training_confirmed:
        errors.append(
            "LLM_NO_TRAINING_CONFIRMED is not true. Real students' work and teachers' notes are sent to the LLM, so it must be a paid / "
            "business tier whose terms say prompts are NOT used for training (a free tier often allows training). "
            "Check your provider's data terms, then set LLM_NO_TRAINING_CONFIRMED=true.")
    if cfg.ocr_provider.lower() != "fake" and not cfg.llm_no_training_confirmed:
        warnings.append("OCR sends textbook pages and students' homework photos to the OCR provider: check its data terms too.")
    if cfg.teacher_signup_mode.lower() not in ("approval", "invite", "open"):
        errors.append("TEACHER_SIGNUP_MODE must be approval, invite or open.")
    elif cfg.teacher_signup_mode.lower() == "open":
        warnings.append("TEACHER_SIGNUP_MODE=open: anyone who finds the site can register as a teacher and spend your AI quota.")
    if cfg.api_domain.startswith("http://") and "localhost" not in cfg.api_domain and "127.0.0.1" not in cfg.api_domain:
        warnings.append("API_DOMAIN is plain http: session cookies need https on a public site.")
    if not cfg.admin_usernames.strip():
        warnings.append("ADMIN_USERNAMES is empty: nobody can use the admin dashboard.")
    if cfg.usage_metering_enabled is False:
        warnings.append("USAGE_METERING_ENABLED=false: no daily caps, no kill switch, no usage records.")
    return errors, warnings


def validate_runtime_config(cfg: Settings | None = None) -> None:
    cfg = cfg or default_settings
    errors, warnings = check_config(cfg)
    for w in warnings:
        logger.warning("Config: %s", w)
    if not errors:
        return
    if cfg.env.lower() == "dev":
        for e in errors:
            logger.warning("Config (ignored in ENV=dev): %s", e)
        return
    raise RuntimeError("Unsafe configuration for ENV=%s:\n  - %s" % (cfg.env, "\n  - ".join(errors)))
