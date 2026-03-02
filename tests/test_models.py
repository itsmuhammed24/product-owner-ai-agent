"""Tests des modèles métier."""

from po_agent.domain.models import BacklogItem, FeedbackItem, Insight, UserStory


def test_feedback_item():
    item = FeedbackItem(
        id="FB-001",
        source="ticket",
        client="Acme",
        segment="mid-market",
        plan="Pro",
        created_at="2026-02-12",
        text="SSO with Azure AD.",
    )
    assert item.id == "FB-001"
    assert item.source == "ticket"


def test_insight():
    i = Insight(
        theme="Auth",
        request="SSO with Azure AD",
        category="feature_request",
        occurrences=5,
        evidence_quotes=["SSO mandatory", "Azure AD minimum"],
        source_feedback_ids=["FB-001", "FB-010"],
    )
    assert i.theme == "Auth"
    assert i.occurrences == 5


def test_backlog_item():
    b = BacklogItem(
        feature="SSO",
        theme="Auth",
        rice_score=480.0,
        reach=500,
        impact=3.0,
        confidence=0.9,
        effort=2.5,
        moscow="Must",
        rationale="Enterprise blocker",
        source_feedback_ids=["FB-001", "FB-010"],
    )
    assert b.moscow == "Must"
    assert b.rice_score == 480.0


def test_user_story():
    us = UserStory(
        title="SSO Azure AD",
        user_story="As an admin I want SSO so that users log in via corp identity",
        acceptance_criteria=["User can log in with Azure AD", "MFA supported"],
        complexity="M",
    )
    assert us.complexity == "M"
    assert len(us.acceptance_criteria) == 2


def test_user_story_acceptance_criteria_dict_normalization():
    """LLM peut retourner acceptance_criteria en [{"given":"...","when":"...","then":"..."}]."""
    raw = {
        "title": "Mute tasks",
        "user_story": "As a user I want to mute tasks",
        "acceptance_criteria": [
            {"given": "A project", "when": "I mute", "then": "It shows Muted"},
            "Plain string criterion",
        ],
        "complexity": "M",
    }
    us = UserStory.model_validate(raw)
    assert all(isinstance(c, str) for c in us.acceptance_criteria)
    assert "Given A project" in us.acceptance_criteria[0]
    assert "Plain string criterion" == us.acceptance_criteria[1]
