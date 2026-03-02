"""Vector store Chroma (optionnel) — RAG persistant cross-sessions."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

log = logging.getLogger("po_agent.vector_store")

# Même modèle que RetrievalAgent (sentence-transformers)
CHROMA_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _chroma_available() -> bool:
    try:
        import chromadb  # noqa: F401

        return True
    except ImportError:
        return False


def _persist_path() -> Path:
    return Path(os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")).resolve()


@lru_cache(maxsize=1)
def _get_client():
    """Client Chroma persistant avec embeddings sentence-transformers (même modèle que RAG)."""
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    from chromadb.utils import embedding_functions

    persist_dir = str(_persist_path())
    _persist_path().mkdir(parents=True, exist_ok=True)

    # Cache local dans le projet (évite ~/.cache)
    if not os.getenv("SENTENCE_TRANSFORMERS_HOME"):
        cache_dir = str(Path(persist_dir).parent / ".cache")
        os.environ["SENTENCE_TRANSFORMERS_HOME"] = cache_dir

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=CHROMA_EMBEDDING_MODEL,
    )
    client = chromadb.PersistentClient(
        path=persist_dir, settings=ChromaSettings(anonymized_telemetry=False)
    )
    return client, ef


def add_to_store(features: List[str], metadatas: Optional[List[dict]] = None) -> None:
    """Ajoute des features au store Chroma (si disponible)."""
    if not _chroma_available() or os.getenv("USE_CHROMA", "").lower() not in ("1", "true", "yes"):
        return
    if not features:
        return
    try:
        import uuid

        client, ef = _get_client()
        coll = client.get_or_create_collection(
            "po_features",
            metadata={"description": "Backlog features for RAG"},
            embedding_function=ef,
        )
        ids = [f"f_{uuid.uuid4().hex[:12]}" for _ in features]
        metadatas = metadatas or [{"feature": f} for f in features]
        coll.upsert(ids=ids, documents=features, metadatas=metadatas)
        log.info("Chroma: upserted %d features", len(features))
    except Exception as e:
        log.warning("Chroma add failed: %s", e)


def query_similar(feature: str, top_k: int = 3) -> List[str]:
    """Retourne les features similaires depuis Chroma (si disponible)."""
    if not _chroma_available() or os.getenv("USE_CHROMA", "").lower() not in ("1", "true", "yes"):
        return []
    try:
        client, ef = _get_client()
        persist_dir = str(_persist_path())
        if not Path(persist_dir).exists():
            return []
        coll = client.get_or_create_collection(
            "po_features",
            metadata={"description": "Backlog features for RAG"},
            embedding_function=ef,
        )
        if coll.count() == 0:
            return []
        results = coll.query(query_texts=[feature], n_results=min(top_k + 1, coll.count()))
        docs = results.get("documents", [[]])
        similar = docs[0] if docs else []
        return [s for s in similar if s != feature][:top_k]
    except Exception as e:
        log.debug("Chroma query failed: %s", e)
        return []
