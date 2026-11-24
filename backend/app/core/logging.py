import logging

from app.core import requestctx

_factory_installed = False


def _install_record_factory() -> None:
    """Every log record gets request_id and user_id, whichever handler or library emits it."""
    global _factory_installed
    if _factory_installed:
        return
    previous = logging.getLogRecordFactory()

    def factory(*args, **kwargs):
        record = previous(*args, **kwargs)
        ctx = requestctx.current()
        record.request_id = ctx.request_id
        record.user_id = ctx.user_id or "-"
        return record

    logging.setLogRecordFactory(factory)
    _factory_installed = True


def setup_logging() -> None:
    _install_record_factory()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s [req=%(request_id)s user=%(user_id)s]: %(message)s",
    )
