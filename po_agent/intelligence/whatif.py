"""What-if — override Impact/Effort/Reach/Confidence, recalc RICE/roadmap."""

from __future__ import annotations

from typing import Any, Dict, List

from po_agent.domain.models import BacklogItem
from po_agent.domain.scoring import assign_moscow_by_quartiles, compute_rice, compute_wsjf
from po_agent.intelligence.roadmap import generate_roadmap


def recalc_backlog_with_override(
    backlog: List[Dict[str, Any]],
    item_index: int,
    *,
    impact: float | None = None,
    effort: float | None = None,
    reach: int | None = None,
    confidence: float | None = None,
) -> Dict[str, Any]:
    """
    Recalcule le backlog avec un override sur un item.
    Retourne {backlog, roadmap} mis à jour.
    """
    items = [BacklogItem.model_validate(b) for b in backlog]
    if item_index < 0 or item_index >= len(items):
        return {"backlog": [b.model_dump() for b in items], "roadmap": generate_roadmap(items)}

    item = items[item_index]
    reach_new = reach if reach is not None else item.reach
    impact_new = impact if impact is not None else item.impact
    confidence_new = confidence if confidence is not None else item.confidence
    effort_new = effort if effort is not None else item.effort

    rice = compute_rice(reach_new, impact_new, confidence_new, effort_new)
    cost_of_delay = reach_new * impact_new * confidence_new
    wsjf = compute_wsjf(cost_of_delay, effort_new)

    new_item = BacklogItem(
        feature=item.feature,
        theme=item.theme,
        rice_score=round(rice, 2),
        reach=reach_new,
        impact=impact_new,
        confidence=confidence_new,
        effort=effort_new,
        moscow="Could",
        rationale=item.rationale,
        source_feedback_ids=item.source_feedback_ids,
        wsjf_score=round(wsjf, 2),
        cost_of_delay=round(cost_of_delay, 2),
    )
    items[item_index] = new_item
    items.sort(key=lambda x: x.rice_score, reverse=True)
    assign_moscow_by_quartiles(items)
    roadmap = generate_roadmap(items)

    return {
        "backlog": [b.model_dump() for b in items],
        "roadmap": {
            "Now": [b.model_dump() for b in roadmap["Now"]],
            "Next": [b.model_dump() for b in roadmap["Next"]],
            "Later": [b.model_dump() for b in roadmap["Later"]],
        },
    }
