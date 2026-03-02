"""PriorityAgent : Insight[] → BacklogItem[] (RICE + MoSCoW + justification LLM)."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from po_agent.domain.models import BacklogItem, Insight, PriorityBatchOutput, PrioritySuggestion
from po_agent.domain.rules import default_confidence_from_occurrences
from po_agent.domain.scoring import assign_moscow_by_quartiles, compute_rice, compute_wsjf
from po_agent.llm.prompts import PRIORITY_AGENT_SYSTEM, PRIORITY_AGENT_USER


def _get_llm_suggestions(insights: List[Insight], llm) -> Dict[int, PrioritySuggestion] | None:
    """Appelle le LLM pour affiner impact/effort/rationale. None si échec."""
    if not insights:
        return {}
    try:
        insights_json = json.dumps(
            [
                {
                    "request": ins.request,
                    "category": ins.category,
                    "occurrences": ins.occurrences,
                    "evidence_quotes": ins.evidence_quotes[:2],
                }
                for ins in insights
            ],
            indent=2,
        )
        user_prompt = PRIORITY_AGENT_USER.format(insights_json=insights_json)
        batch = llm.complete_structured(
            system=PRIORITY_AGENT_SYSTEM,
            user=user_prompt,
            model=PriorityBatchOutput,
        )
        items = batch.items if hasattr(batch, "items") else []
        return {i: s for i, s in enumerate(items)}
    except Exception as e:
        logging.getLogger(__name__).warning("Priority LLM suggestions failed: %s", e, exc_info=True)
        return None


def estimate_effort_from_category(category: str) -> float:
    """Estimation heuristique de l'effort par catégorie."""
    if category == "compliance":
        return 8.0
    elif category == "performance":
        return 5.0
    elif category == "bug":
        return 2.0
    else:
        return 4.0


def estimate_impact_from_category(category: str) -> float:
    """Impact par défaut selon la catégorie."""
    if category in ["compliance", "performance"]:
        return 3.0
    elif category == "feature_request":
        return 2.0
    else:
        return 1.5


def build_rationale(insight: Insight, rice: float, moscow: str) -> str:
    """Justification par défaut (fallback heuristique)."""
    return (
        f"This request appears {insight.occurrences} times. "
        f"Category: {insight.category}. "
        f"RICE score: {rice:.2f}. "
        f"Prioritized as {moscow} due to estimated impact and effort."
    )


def prioritize_features(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforme Insight[] → BacklogItem[] priorisés.
    Si LLM dispo : utilise suggestions impact/effort/rationale.
    """
    insights: List[Insight] = state.get("insights", [])
    llm = state.get("options", {}).get("llm")
    suggestions: Dict[int, PrioritySuggestion] | None = None

    if llm is not None:
        suggestions = _get_llm_suggestions(insights, llm)
        if suggestions is None:
            suggestions = {}

    backlog: List[BacklogItem] = []

    for i, ins in enumerate(insights):
        reach = ins.occurrences
        confidence = default_confidence_from_occurrences(ins.occurrences)

        sug = (suggestions or {}).get(i) if suggestions else None
        if sug:
            impact = max(1.0, min(3.0, sug.impact))
            effort = max(1.0, min(10.0, sug.effort))
            rationale = sug.rationale
        else:
            impact = estimate_impact_from_category(ins.category)
            effort = estimate_effort_from_category(ins.category)
            _rice = compute_rice(reach, impact, confidence, effort)
            rationale = build_rationale(ins, _rice, "Could")

        rice = compute_rice(reach, impact, confidence, effort)
        cost_of_delay = reach * impact * confidence
        wsjf = compute_wsjf(cost_of_delay, effort)

        backlog.append(
            BacklogItem(
                feature=ins.request,
                theme=ins.theme,
                rice_score=rice,
                reach=reach,
                impact=impact,
                confidence=confidence,
                effort=effort,
                moscow="Could",
                rationale=rationale,
                source_feedback_ids=ins.source_feedback_ids,
                wsjf_score=round(wsjf, 2),
                cost_of_delay=round(cost_of_delay, 2),
            )
        )

    backlog.sort(key=lambda x: x.rice_score, reverse=True)
    assign_moscow_by_quartiles(backlog)
    for item in backlog:
        item.rationale = build_rationale(
            next(ins for ins in insights if ins.request == item.feature),
            item.rice_score,
            item.moscow,
        )

    state["backlog"] = backlog
    return state
