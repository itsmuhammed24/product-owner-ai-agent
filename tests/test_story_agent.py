"""Tests StoryAgent — sans appeler le vrai LLM."""

from po_agent.agents.story_agent import generate_stories
from po_agent.domain.models import BacklogItem
from tests.mock_llm import MockLLM


def test_story_agent_generates_stories():
    state = {
        "feedback": [],
        "insights": [],
        "backlog": [
            BacklogItem(
                feature="add sso",
                theme="feature_request",
                rice_score=900.0,
                reach=10,
                impact=2.0,
                confidence=0.9,
                effort=2.0,
                moscow="Must",
                rationale="Test rationale",
                source_feedback_ids=["FB-001", "FB-010"],
            )
        ],
        "stories": [],
        "options": {"llm": MockLLM()},
        "errors": [],
    }

    out = generate_stories(state)
    stories = out["stories"]

    assert len(stories) == 1
    assert stories[0].user_story.startswith("As a ")
    assert 4 <= len(stories[0].acceptance_criteria) <= 7
    assert stories[0].complexity in {"XS", "S", "M", "L", "XL"}


def test_story_agent_multiple_items():
    """Plusieurs BacklogItems → plusieurs UserStories."""
    state = {
        "feedback": [],
        "insights": [],
        "backlog": [
            BacklogItem(
                feature="add sso",
                theme="feature_request",
                rice_score=900.0,
                reach=10,
                impact=2.0,
                confidence=0.9,
                effort=2.0,
                moscow="Must",
                rationale="Test",
                source_feedback_ids=["FB-001"],
            ),
            BacklogItem(
                feature="export pdf",
                theme="feature_request",
                rice_score=200.0,
                reach=5,
                impact=2.0,
                confidence=0.8,
                effort=3.0,
                moscow="Could",
                rationale="Test",
                source_feedback_ids=["FB-002"],
            ),
        ],
        "stories": [],
        "options": {"llm": MockLLM()},
        "errors": [],
    }

    out = generate_stories(state)
    assert len(out["stories"]) == 2


def test_story_agent_empty_backlog():
    """Backlog vide → stories vide."""
    state = {
        "backlog": [],
        "stories": [],
        "options": {"llm": MockLLM()},
    }
    out = generate_stories(state)
    assert out["stories"] == []
