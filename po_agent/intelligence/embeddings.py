"""Embeddings — similarité cosinus, clustering (sentence-transformers / OpenAI)."""

import logging
import os
from typing import List, Optional

from openai import OpenAI


def _get_api_key() -> Optional[str]:
    return (os.getenv("OPENAI_API_KEY") or "").strip()


def embeddings_available() -> bool:
    """True si les embeddings sont utilisables (clé API)."""
    return bool(_get_api_key())


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Similarité cosinus entre deux vecteurs."""
    import math

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingService:
    """Service d'embeddings OpenAI."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key or _get_api_key() or "sk-dummy")
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Retourne les vecteurs d'embedding pour une liste de textes."""
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [r.embedding for r in response.data]


def cluster_requests(requests: List[str], threshold: float = 0.85) -> List[List[str]]:
    """
    Regroupe les requêtes par similarité sémantique.
    'Add SSO', 'Support SAML login', 'Azure AD authentication' → 1 cluster.
    """
    if not requests:
        return []
    try:
        service = EmbeddingService()
        vectors = service.embed(requests)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Embeddings API indisponible, fallback 1 cluster/requête: %s", e, exc_info=True
        )
        return [[r] for r in requests]

    clusters: List[List[str]] = []
    used: set[int] = set()

    for i, vec in enumerate(vectors):
        if i in used:
            continue

        cluster = [requests[i]]
        used.add(i)

        for j in range(i + 1, len(vectors)):
            if j in used:
                continue
            sim = cosine_similarity(vec, vectors[j])
            if sim >= threshold:
                cluster.append(requests[j])
                used.add(j)

        clusters.append(cluster)

    return clusters
