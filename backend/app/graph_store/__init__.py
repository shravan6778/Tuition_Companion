import threading
from typing import Optional

from app.core.config import settings

from .base import GraphStore, GraphStoreError
from .fake_store import FakeGraphStore

FAKE_STORE = FakeGraphStore()  # one per process, like a real server (tests clear it between runs)
_cache: dict = {}
_lock = threading.Lock()


def get_graph_store() -> Optional[GraphStore]:
    """None means the graph store is switched off (GRAPH_STORE_PROVIDER=none): the pipeline skips that stage.
    The Memgraph store is cached per process (its driver pools connections and is thread-safe)."""
    kind = settings.graph_store_provider.lower()
    if kind == "fake":
        return FAKE_STORE
    if kind == "memgraph":
        key = (
            settings.memgraph_uri, settings.memgraph_user, settings.memgraph_password, settings.embedding_dim,
            settings.memgraph_vector_capacity, settings.memgraph_vector_metric,
        )
        with _lock:
            if key not in _cache:
                from .memgraph_store import MemgraphStore  # imported late: the driver is only needed when used

                _cache[key] = MemgraphStore(
                    settings.memgraph_uri, settings.memgraph_user, settings.memgraph_password,
                    dim=settings.embedding_dim, capacity=settings.memgraph_vector_capacity,
                    metric=settings.memgraph_vector_metric, batch=settings.graph_sync_batch,
                    max_candidates=settings.graph_search_max_candidates,
                )
            return _cache[key]
    return None


def close_graph_stores() -> None:
    with _lock:
        for store in _cache.values():
            store.close()
        _cache.clear()


__all__ = ["FAKE_STORE", "GraphStore", "GraphStoreError", "close_graph_stores", "get_graph_store"]
