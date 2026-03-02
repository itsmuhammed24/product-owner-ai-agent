"""SynthesisAgent : Backlog + Roadmap -> Executive Summary."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from po_agent.domain.models import BacklogItem, RoadmapSummary
from po_agent.intelligence.roadmap import generate_roadmap


def generate_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Genere un executive summary de la roadmap."""
    backlog: List[BacklogItem] = state.get("backlog", [])
    llm = state.get("options", {}).get("llm")
    roadmap = generate_roadmap(backlog)

    now_features = [b.feature for b in roadmap["Now"]]
    next_features = [b.feature for b in roadmap["Next"]]
    later_features = [b.feature for b in roadmap["Later"]]

    try:
        if llm is not None:
            from po_agent.llm.prompts import SYNTHESIS_AGENT_SYSTEM, SYNTHESIS_AGENT_USER

            user_prompt = SYNTHESIS_AGENT_USER.format(
                now_list=", ".join(now_features) or "-",
                next_list=", ".join(next_features) or "-",
                later_list=", ".join(later_features) or "-",
            )
            out = llm.complete_structured(
                system=SYNTHESIS_AGENT_SYSTEM,
                user=user_prompt,
                model=RoadmapSummary,
            )
            summary = out.summary if hasattr(out, "summary") else str(out)
        else:
            summary = _fallback_summary(roadmap)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "LLM synthesis failed, using fallback: %s", e, exc_info=True
        )
        summary = _fallback_summary(roadmap)

    state["options"]["roadmap_summary"] = summary
    return state


def _fallback_summary(roadmap: Dict[str, List[BacklogItem]]) -> str:
    now = roadmap.get("Now", [])
    next_items = roadmap.get("Next", [])
    parts = []
    if now:
        parts.append("Priorites immediates: " + ", ".join(b.feature for b in now[:5]) + ".")
    if next_items:
        parts.append("Prochaines: " + ", ".join(b.feature for b in next_items[:5]) + ".")
    if not parts:
        parts.append("Backlog vide.")
    return " ".join(parts)
