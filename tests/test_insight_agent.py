"""Tests InsightAgent — sans LLM."""

from po_agent.agents.insight_agent import extract_insights, normalize_request
from po_agent.domain.models import AnalyzedFeedback


def test_normalize_request():
    """Normalisation lowercase + strip."""
    assert normalize_request("  Add SSO  ") == "add sso"
    assert normalize_request("ADD SSO") == "add sso"


def test_insight_grouping():
    """Deux feedbacks avec la même requête → 1 insight, occurrences=2."""
    analyzed = [
        AnalyzedFeedback(
            feedback_id="FB-001",
            category="feature_request",
            summary="Need SSO",
            severity=4,
            extracted_requests=["Add SSO"],
            evidence_quotes=["SSO mandatory"],
        ),
        AnalyzedFeedback(
            feedback_id="FB-002",
            category="feature_request",
            summary="SSO required",
            severity=5,
            extracted_requests=["Add SSO"],
            evidence_quotes=["Need SAML SSO"],
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
    assert insights[0].occurrences == 2
    assert "FB-001" in insights[0].source_feedback_ids
    assert "FB-002" in insights[0].source_feedback_ids


def test_insight_empty_analyzed():
    """Analyzed_feedback vide → insights vide."""
    state = {
        "feedback": [],
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"analyzed_feedback": []},
        "errors": [],
    }
    out = extract_insights(state)
    assert out["insights"] == []


def test_insight_skips_empty_requests():
    """Feedback sans extracted_requests → ignoré."""
    analyzed = [
        AnalyzedFeedback(
            feedback_id="FB-001",
            category="feature_request",
            summary="Vague feedback",
            severity=2,
            extracted_requests=[],
            evidence_quotes=[],
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
    assert out["insights"] == []


def test_insight_separate_requests():
    """Requêtes différentes → insights séparés."""
    analyzed = [
        AnalyzedFeedback(
            feedback_id="FB-001",
            category="feature_request",
            summary="Need SSO",
            severity=4,
            extracted_requests=["Add SSO"],
            evidence_quotes=[],
        ),
        AnalyzedFeedback(
            feedback_id="FB-002",
            category="feature_request",
            summary="Need export",
            severity=3,
            extracted_requests=["Export to PDF"],
            evidence_quotes=[],
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

    assert len(insights) == 2
    requests = {i.request for i in insights}
    assert "add sso" in requests
    assert "export to pdf" in requests
