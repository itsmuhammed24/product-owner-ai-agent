"""Tests FeedbackAgent — sans appeler le vrai LLM."""

from po_agent.agents.feedback_agent import analyze_feedback
from po_agent.domain.models import FeedbackItem
from tests.mock_llm import MockLLM


def test_feedback_agent_contract():
    state = {
        "feedback": [
            FeedbackItem(
                id="FB-001",
                source="ticket",
                client="Acme",
                segment="mid-market",
                plan="Pro",
                created_at="2026-02-12",
                text="SSO with Azure AD is mandatory for us. We can't roll out without it.",
            )
        ],
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"llm": MockLLM()},
        "errors": [],
    }

    out = analyze_feedback(state)
    analyzed = out["options"]["analyzed_feedback"]

    assert len(analyzed) == 1
    assert analyzed[0].feedback_id == "FB-001"
    assert analyzed[0].category in {
        "bug",
        "feature_request",
        "ux_pain",
        "performance",
        "pricing",
        "compliance",
        "other",
    }
    assert 1 <= analyzed[0].severity <= 5
