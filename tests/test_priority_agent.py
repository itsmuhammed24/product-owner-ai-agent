"""Tests PriorityAgent — sans LLM."""

from po_agent.agents.priority_agent import (
    estimate_effort_from_category,
    estimate_impact_from_category,
    prioritize_features,
)
from po_agent.domain.models import Insight


def test_priority_generation():
    insights = [
        Insight(
            theme="feature_request",
            request="Add SSO",
            category="feature_request",
            occurrences=10,
            evidence_quotes=["SSO mandatory"],
            source_feedback_ids=["FB-001", "FB-010"],
        )
    ]

    state = {
        "feedback": [],
        "insights": insights,
        "backlog": [],
        "stories": [],
        "options": {},
        "errors": [],
    }

    out = prioritize_features(state)

    backlog = out["backlog"]

    assert len(backlog) == 1
    assert backlog[0].rice_score > 0
    assert backlog[0].moscow in ["Must", "Should", "Could", "Wont"]
    assert "RICE score" in backlog[0].rationale


def test_estimate_effort_from_category():
    assert estimate_effort_from_category("compliance") == 8.0
    assert estimate_effort_from_category("performance") == 5.0
    assert estimate_effort_from_category("bug") == 2.0
    assert estimate_effort_from_category("feature_request") == 4.0


def test_estimate_impact_from_category():
    assert estimate_impact_from_category("compliance") == 3.0
    assert estimate_impact_from_category("performance") == 3.0
    assert estimate_impact_from_category("feature_request") == 2.0
    assert estimate_impact_from_category("ux_pain") == 1.5


def test_priority_sort_by_rice():
    """Le backlog est trié par RICE décroissant."""
    insights = [
        Insight(
            theme="feature_request",
            request="Low priority",
            category="other",
            occurrences=1,
            evidence_quotes=[],
            source_feedback_ids=["FB-001"],
        ),
        Insight(
            theme="feature_request",
            request="High priority",
            category="feature_request",
            occurrences=15,
            evidence_quotes=[],
            source_feedback_ids=["FB-002", "FB-003"],
        ),
    ]

    state = {"insights": insights, "backlog": []}
    out = prioritize_features(state)

    assert out["backlog"][0].feature == "High priority"
    assert out["backlog"][0].rice_score > out["backlog"][1].rice_score


def test_priority_empty_insights():
    """Insights vide → backlog vide."""
    state = {"insights": [], "backlog": []}
    out = prioritize_features(state)
    assert out["backlog"] == []
