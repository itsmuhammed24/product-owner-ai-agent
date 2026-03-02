"""Tests de déduplication dans InsightAgent (feedback_ids)."""

from po_agent.agents.insight_agent import extract_insights
from po_agent.domain.models import AnalyzedFeedback


def test_deduplicate_feedback_ids_same_feedback_multiple_requests():
    """Un même feedback avec plusieurs extracted_requests identiques → feedback_id dédupliqué."""
    analyzed = [
        AnalyzedFeedback(
            feedback_id="FB-001",
            category="feature_request",
            summary="Need SSO and SSO",
            severity=4,
            extracted_requests=["Add SSO", "add sso"],  # normalisées = même cluster
            evidence_quotes=["SSO please"],
        ),
    ]

    state = {
        "feedback": [],
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"analyzed_feedback": analyzed},
        "errors": [],
    }

    out = extract_insights(state)
    insights = out["insights"]

    assert len(insights) == 1
    assert insights[0].occurrences == 1
    assert insights[0].source_feedback_ids == ["FB-001"]
