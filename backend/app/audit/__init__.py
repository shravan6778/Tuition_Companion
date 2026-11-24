"""Audit log of administrative and sensitive actions. See service.py."""
from .service import record, record_now

__all__ = ["record", "record_now"]
