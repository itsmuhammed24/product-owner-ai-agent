"""Pipeline entrypoint — run_full_pipeline()."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from po_agent.agents.orchestrator import run_agent, stream_agent
from po_agent.domain.models import FeedbackItem
from po_agent.intelligence.roadmap import generate_roadmap

SMALL_FEEDBACK_THRESHOLD = 10
LOG = logging.getLogger("po_agent.pipeline")


def _prepare_pipeline_options(
    feedback: List[FeedbackItem],
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Prépare les options du pipeline (product_name, target_segment, max_critique_passes)."""
    from po_agent.core.config import get_settings

    s = get_settings()
    opts = dict(options or {})
    opts.setdefault("product_name", s.product_name)
    opts.setdefault("target_segment", s.target_segment)
    if len(feedback) <= SMALL_FEEDBACK_THRESHOLD:
        opts.setdefault("max_critique_passes", 1)
    return opts


def run_full_pipeline(
    feedback: List[FeedbackItem],
    *,
    llm,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Exécute le workflow complet et retourne un dict JSON-serializable pour l'API.
    Valide les entrées (limite count, truncate text) avant traitement.
    """
    from po_agent.core.config import get_settings
    from po_agent.core.validation import validate_and_prepare_feedback

    s = get_settings()
    feedback, val_warnings = validate_and_prepare_feedback(
        feedback,
        max_count=s.max_feedbacks,
        max_text_length=s.max_text_length,
    )
    if val_warnings:
        for w in val_warnings:
            LOG.warning("Validation: %s", w)

    opts = _prepare_pipeline_options(feedback, options)
    t0 = time.time()
    state = run_agent(feedback, llm=llm, options=opts)
    elapsed = time.time() - t0
    LOG.info("Pipeline completed in %.2fs (%d feedbacks)", elapsed, len(feedback))
    backlog = state["backlog"]
    roadmap = generate_roadmap(backlog)
    summary = state.get("options", {}).get("roadmap_summary", "")

    stories_before = state.get("options", {}).get("stories_before_critique")

    return {
        "insights": [i.model_dump() for i in state["insights"]],
        "backlog": [b.model_dump() for b in backlog],
        "roadmap": {
            "Now": [b.model_dump() for b in roadmap["Now"]],
            "Next": [b.model_dump() for b in roadmap["Next"]],
            "Later": [b.model_dump() for b in roadmap["Later"]],
        },
        "stories": [s.model_dump() if s is not None else None for s in state["stories"]],
        "stories_before_critique": stories_before,
        "summary": summary,
        "errors": state["errors"] + val_warnings,
    }


def run_partial_pipeline(
    feedback: List[FeedbackItem],
    *,
    llm,
    stop_at: str = "insights",
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Pipeline partiel — human-in-the-loop. stop_at: insights | backlog."""
    from po_agent.agents.feedback_agent import analyze_feedback
    from po_agent.agents.insight_agent import extract_insights
    from po_agent.agents.priority_agent import prioritize_features
    from po_agent.core.config import get_settings
    from po_agent.core.validation import validate_and_prepare_feedback

    s = get_settings()
    feedback, val_warnings = validate_and_prepare_feedback(
        feedback, max_count=s.max_feedbacks, max_text_length=s.max_text_length
    )
    opts = _prepare_pipeline_options(feedback, options)
    state = {
        "feedback": feedback,
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"llm": llm, **opts},
        "errors": val_warnings,
    }
    state = analyze_feedback(state)
    state = extract_insights(state)
    if stop_at == "insights":
        return {
            "insights": [i.model_dump() for i in state["insights"]],
            "analyzed_count": len(state.get("options", {}).get("analyzed_feedback", [])),
            "errors": state["errors"],
            "partial": True,
        }
    state = prioritize_features(state)
    if stop_at == "backlog":
        backlog = state["backlog"]
        roadmap = generate_roadmap(backlog)
        return {
            "insights": [i.model_dump() for i in state["insights"]],
            "backlog": [b.model_dump() for b in backlog],
            "roadmap": {
                "Now": [b.model_dump() for b in roadmap["Now"]],
                "Next": [b.model_dump() for b in roadmap["Next"]],
                "Later": [b.model_dump() for b in roadmap["Later"]],
            },
            "errors": state["errors"],
            "partial": True,
        }
    return {"insights": [], "errors": ["stop_at invalide"], "partial": True}


def run_full_pipeline_stream(
    feedback: List[FeedbackItem],
    *,
    llm,
    options: Optional[Dict[str, Any]] = None,
):
    """Génère des événements (étape, données) pour streaming SSE."""
    from po_agent.core.config import get_settings
    from po_agent.core.validation import validate_and_prepare_feedback

    s = get_settings()
    feedback, val_warnings = validate_and_prepare_feedback(
        feedback, max_count=s.max_feedbacks, max_text_length=s.max_text_length
    )
    if val_warnings:
        for w in val_warnings:
            LOG.warning("Validation: %s", w)

    opts = _prepare_pipeline_options(feedback, options)
    backlog = []
    insights = []
    stories = []
    errors = []

    for node_name, state_update in stream_agent(feedback, llm=llm, options=opts):
        if node_name == "analyze_feedback":
            n = state_update.get("options", {}).get("analyzed_feedback", [])
            yield ("analyze", {"count": len(n)})
        elif node_name == "extract_insights":
            insights = state_update.get("insights", [])
            yield (
                "insights",
                {"count": len(insights), "insights": [i.model_dump() for i in insights]},
            )
        elif node_name == "prioritize_features":
            backlog = state_update.get("backlog", [])
            yield ("backlog", {"count": len(backlog), "backlog": [b.model_dump() for b in backlog]})
        elif node_name == "enrich_retrieval":
            yield ("retrieval", {})
        elif node_name == "generate_stories":
            stories = state_update.get("stories", [])
            errors = state_update.get("errors", [])
            stories_clean = [s for s in stories if s is not None]
            yield (
                "stories",
                {"count": len(stories_clean), "stories": [s.model_dump() for s in stories_clean]},
            )
        elif node_name == "critique_stories":
            stories = state_update.get("stories", [])
            yield ("critique", {})
        elif node_name == "generate_summary":
            summary = state_update.get("options", {}).get("roadmap_summary", "")
            errors = state_update.get("errors", errors)
            roadmap = generate_roadmap(backlog)
            yield (
                "done",
                {
                    "insights": [i.model_dump() for i in insights],
                    "backlog": [b.model_dump() for b in backlog],
                    "roadmap": {
                        "Now": [b.model_dump() for b in roadmap["Now"]],
                        "Next": [b.model_dump() for b in roadmap["Next"]],
                        "Later": [b.model_dump() for b in roadmap["Later"]],
                    },
                    "stories": [s.model_dump() if s is not None else None for s in stories],
                    "summary": summary,
                    "errors": errors + val_warnings,
                },
            )
