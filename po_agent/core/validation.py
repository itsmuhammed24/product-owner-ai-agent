"""Validation des entrées pipeline — limites et sanitization."""

from __future__ import annotations

from typing import List

from po_agent.domain.models import FeedbackItem


def validate_and_prepare_feedback(
    feedback: List[FeedbackItem],
    max_count: int = 100,
    max_text_length: int = 10_000,
) -> tuple[List[FeedbackItem], List[str]]:
    """Limite count, tronque text. Retourne (feedback, warnings)."""
    warnings: List[str] = []
    original_count = len(feedback)
    if original_count > max_count:
        feedback = feedback[:max_count]
        warnings.append(f"Limite à {max_count} feedbacks (reçu {original_count})")

    prepared: List[FeedbackItem] = []
    for fb in feedback:
        text = fb.text or ""
        if len(text) > max_text_length:
            text = text[:max_text_length] + " [tronqué]"
            warnings.append(f"Feedback {fb.id}: text tronqué à {max_text_length} caractères")
        prepared.append(
            FeedbackItem(
                id=fb.id,
                source=fb.source,
                client=fb.client,
                segment=fb.segment,
                plan=fb.plan,
                created_at=fb.created_at,
                text=text,
            )
        )
    return prepared, warnings
