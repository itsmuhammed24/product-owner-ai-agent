"""RetrievalAgent : RAG — enrichit le contexte du StoryAgent avec features similaires."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List

from po_agent.domain.models import BacklogItem

log = logging.getLogger("po_agent.retrieval_agent")

TOP_K = 3
SIMILARITY_THRESHOLD = 0.5
_EMBEDDING_CACHE_MAXSIZE = 512


_model_cache: Any = None


def _get_embedding_model():
    """Charge le modèle une fois et le met en cache."""
    global _model_cache
    if _model_cache is None:
        from sentence_transformers import SentenceTransformer

        _model_cache = SentenceTransformer("all-MiniLM-L6-v2")
    return _model_cache


@lru_cache(maxsize=_EMBEDDING_CACHE_MAXSIZE)
def _embed_one_cached(text: str):
    """Cache LRU par texte (hashable). Nécessite _get_embedding_model() appelé avant."""
    model = _get_embedding_model()
    import numpy as np

    v = model.encode(text, convert_to_numpy=True)
    return tuple(v.tolist())  # tuple hashable pour lru_cache


def _encode_cached(model, features: List[str]):
    """Encode les features en vectors, avec cache LRU par texte."""
    import numpy as np

    vectors = [np.array(_embed_one_cached(f)) for f in features]
    return np.array(vectors)


def _embed_and_retrieve(
    features: List[str], top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD
) -> Dict[int, List[str]]:
    """
    Pour chaque feature, retourne les top-k features similaires (hors elle-même).
    Retourne {idx: [feature_similar_1, ...]}.
    """
    try:
        import numpy as np

        _get_embedding_model()
    except ImportError:
        log.debug("sentence-transformers non installé — RAG désactivé")
        return {}

    if len(features) < 2:
        return {}

    try:
        model = _get_embedding_model()
        vectors = _encode_cached(model, features)
    except Exception as e:
        log.warning("Embedding RAG failed: %s", e)
        return {}

    result: Dict[int, List[str]] = {}
    for i in range(len(features)):
        sims = np.dot(vectors, vectors[i]) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(vectors[i]) + 1e-9
        )
        # Exclure soi-même, trier par similarité décroissante
        indices = np.argsort(sims)[::-1]
        similar: List[str] = []
        for j in indices:
            if j == i:
                continue
            if sims[j] >= threshold and len(similar) < top_k:
                similar.append(features[j])
        if similar:
            result[i] = similar

    return result


def enrich_backlog_with_retrieval(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrichit le backlog avec des features similaires (RAG).
    - In-memory : similarité entre features du backlog actuel (sentence-transformers).
    - Si USE_CHROMA=true : enrichit avec features historiques depuis Chroma.
    Stocke dans state["options"]["backlog_related_features"] = {idx: [str, ...]}.
    """
    backlog: List[BacklogItem] = state.get("backlog", [])
    opts = state.get("options", {})

    if not backlog or len(backlog) < 2:
        opts["backlog_related_features"] = {}
        return state

    features = [item.feature for item in backlog]
    related = _embed_and_retrieve(features, top_k=TOP_K, threshold=SIMILARITY_THRESHOLD)

    if os.getenv("USE_CHROMA", "").lower() in ("1", "true", "yes"):
        try:
            from po_agent.intelligence.vector_store import add_to_store, query_similar

            add_to_store(
                features,
                metadatas=[
                    {"feature": f, "rationale": getattr(b, "rationale", "")[:200]}
                    for f, b in zip(features, backlog)
                ],
            )
            for i in range(len(features)):
                from_chroma = query_similar(features[i], top_k=TOP_K)
                existing = set(related.get(i, []))
                for s in from_chroma:
                    if s not in existing and s != features[i]:
                        existing.add(s)
                        if len(existing) >= TOP_K:
                            break
                if existing:
                    related[i] = list(existing)[:TOP_K]
        except Exception as e:
            log.debug("Chroma enrichment skip: %s", e)

    opts["backlog_related_features"] = related
    if related:
        log.info("RAG: enriched %d backlog items with similar features", len(related))

    return state
