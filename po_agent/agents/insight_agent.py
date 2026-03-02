"""InsightAgent : AnalyzedFeedback[] → Insight[] (clustering & consolidation)."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from po_agent.domain.models import AnalyzedFeedback, Insight

try:
    from po_agent.intelligence.embeddings import (
        cluster_requests,
        embeddings_available,
    )
except ImportError:

    def embeddings_available() -> bool:
        return False

    def cluster_requests(requests: List[str], **kwargs: Any) -> List[List[str]]:
        return [[r] for r in requests]


def normalize_request(text: str) -> str:
    """Normalise une requête pour clustering (lowercase, strip)."""
    return text.strip().lower()


def _collect_request_to_feedback(
    analyzed: List[AnalyzedFeedback],
) -> Dict[str, List[Tuple[AnalyzedFeedback, str]]]:
    """Collecte (req_normalized) -> [(fb, req_original), ...]."""
    out: Dict[str, List[Tuple[AnalyzedFeedback, str]]] = defaultdict(list)
    for fb in analyzed:
        if not fb.extracted_requests:
            continue
        for req in fb.extracted_requests:
            key = normalize_request(req)
            out[key].append((fb, req))
    return dict(out)


def _merge_with_semantic_clustering(
    req_to_feedback: Dict[str, List[Tuple[AnalyzedFeedback, str]]],
    threshold: float = 0.82,
) -> List[List[str]]:
    """
    Si embeddings dispo : cluster sémantique des requêtes.
    Sinon : 1 cluster par requête (comportement actuel).
    """
    requests = list(req_to_feedback.keys())
    if not requests:
        return []

    use_embeddings = embeddings_available()

    if use_embeddings:
        try:
            return cluster_requests(requests, threshold=threshold)
        except Exception as e:
            logging.getLogger(__name__).warning(
                "Clustering sémantique échoué, fallback 1 cluster/requête: %s", e, exc_info=True
            )

    return [[r] for r in requests]


def extract_insights(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Regroupe les feedbacks analysés par extracted_requests, consolide en Insight.
    Utilise le clustering sémantique (embeddings) si disponible.
    """
    analyzed: List[AnalyzedFeedback] = state["options"].get("analyzed_feedback", [])

    req_to_feedback = _collect_request_to_feedback(analyzed)
    if not req_to_feedback:
        state["insights"] = []
        return state

    merged_clusters = _merge_with_semantic_clustering(req_to_feedback)

    insights: List[Insight] = []

    for cluster in merged_clusters:
        if not cluster:
            continue

        all_items: List[Tuple[AnalyzedFeedback, str]] = []
        for req_key in cluster:
            all_items.extend(req_to_feedback.get(req_key, []))

        if not all_items:
            continue

        first_fb, first_req = all_items[0]
        feedback_ids = list(dict.fromkeys(fb.feedback_id for fb, _ in all_items))
        evidence = [q for fb, _ in all_items for q in fb.evidence_quotes][:3]
        canonical_request = cluster[0]

        insights.append(
            Insight(
                theme=first_fb.category,
                request=canonical_request,
                category=first_fb.category,
                occurrences=len(feedback_ids),
                evidence_quotes=evidence,
                source_feedback_ids=feedback_ids,
            )
        )

    state["insights"] = insights
    return state
