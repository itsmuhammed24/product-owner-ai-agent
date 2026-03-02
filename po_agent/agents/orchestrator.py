"""Orchestrateur LangGraph — workflow agentic complet."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from po_agent.agents.critique_agent import critique_and_refine_stories
from po_agent.agents.feedback_agent import analyze_feedback
from po_agent.agents.insight_agent import extract_insights
from po_agent.agents.priority_agent import prioritize_features
from po_agent.agents.retrieval_agent import enrich_backlog_with_retrieval
from po_agent.agents.story_agent import generate_stories
from po_agent.agents.synthesis_agent import generate_summary
from po_agent.domain.models import BacklogItem, FeedbackItem, Insight, UserStory

log = logging.getLogger("po_agent.orchestrator")

DEFAULT_MAX_CRITIQUE_PASSES = 2


def _route_after_critique(state: Dict[str, Any]) -> str:
    """Conditional edge : reboucle critique si refinées et < max_critique_passes."""
    opts = state.get("options", {})
    refined = opts.get("critique_refined_count", 0)
    pass_count = opts.get("critique_pass", 0)
    max_passes = opts.get("max_critique_passes", DEFAULT_MAX_CRITIQUE_PASSES)
    if refined > 0 and pass_count < max_passes:
        log.info(
            "Reasoning loop: re-critique (%d refined, pass %d/%d)", refined, pass_count, max_passes
        )
        return "critique_stories"
    return "generate_summary"


def _with_timing(name: str, fn: Callable[[Dict], Dict]) -> Callable[[Dict], Dict]:
    """Wrap un nœud pour logger la durée."""

    def wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.perf_counter()
        out = fn(state)
        elapsed = time.perf_counter() - t0
        n = (
            len(out.get("insights", []))
            or len(out.get("backlog", []))
            or len(out.get("stories", []))
            or len((out.get("options") or {}).get("analyzed_feedback", []))
        )
        log.info("[%s] %.2fs n=%s", name, elapsed, n)
        return out

    return wrapped


class AgentState(TypedDict):
    feedback: List[FeedbackItem]
    insights: List[Insight]
    backlog: List[BacklogItem]
    stories: List[UserStory]
    options: Dict[str, Any]
    errors: List[str]


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("analyze_feedback", _with_timing("analyze_feedback", analyze_feedback))
    g.add_node("extract_insights", _with_timing("extract_insights", extract_insights))
    g.add_node("prioritize_features", _with_timing("prioritize_features", prioritize_features))
    g.add_node("enrich_retrieval", _with_timing("enrich_retrieval", enrich_backlog_with_retrieval))
    g.add_node("generate_stories", _with_timing("generate_stories", generate_stories))
    g.add_node("critique_stories", _with_timing("critique_stories", critique_and_refine_stories))
    g.add_node("generate_summary", _with_timing("generate_summary", generate_summary))

    g.set_entry_point("analyze_feedback")
    g.add_edge("analyze_feedback", "extract_insights")
    g.add_edge("extract_insights", "prioritize_features")
    g.add_edge("prioritize_features", "enrich_retrieval")
    g.add_edge("enrich_retrieval", "generate_stories")
    g.add_edge("generate_stories", "critique_stories")
    g.add_conditional_edges(
        "critique_stories",
        _route_after_critique,
        {"critique_stories": "critique_stories", "generate_summary": "generate_summary"},
    )
    g.add_edge("generate_summary", END)

    return g.compile()


GRAPH = build_graph()


def run_agent(
    feedback: List[FeedbackItem],
    *,
    llm,
    options: Optional[Dict[str, Any]] = None,
) -> AgentState:
    state: AgentState = {
        "feedback": feedback,
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"llm": llm, **(options or {})},
        "errors": [],
    }
    return GRAPH.invoke(state)


def stream_agent(
    feedback: List[FeedbackItem],
    *,
    llm,
    options: Optional[Dict[str, Any]] = None,
):
    """Génère (node_name, state_update) à chaque étape."""
    state: AgentState = {
        "feedback": feedback,
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"llm": llm, **(options or {})},
        "errors": [],
    }
    for node_name, state_update in GRAPH.stream(state):
        yield node_name, state_update
