"""Tests SynthesisAgent."""

from po_agent.agents.synthesis_agent import _fallback_summary, generate_summary
from po_agent.domain.models import BacklogItem


def test_fallback_summary():
    roadmap = {
        "Now": [
            BacklogItem(
                feature="Add SSO",
                theme="Auth",
                rice_score=10,
                reach=5,
                impact=2,
                confidence=0.8,
                effort=4,
                moscow="Must",
                rationale="High demand",
                source_feedback_ids=["F1"],
            ),
        ],
        "Next": [],
        "Later": [],
    }
    s = _fallback_summary(roadmap)
    assert "SSO" in s
    assert "Priorites" in s or "immediates" in s


def test_generate_summary_no_llm():
    state = {
        "backlog": [
            BacklogItem(
                feature="Feature A",
                theme="Theme",
                rice_score=8,
                reach=3,
                impact=2,
                confidence=0.7,
                effort=2,
                moscow="Should",
                rationale="Test",
                source_feedback_ids=[],
            ),
        ],
        "options": {},
    }
    out = generate_summary(state)
    assert "roadmap_summary" in out["options"]
    assert len(out["options"]["roadmap_summary"]) > 0


def test_generate_summary_with_mock_llm():
    from tests.mock_llm import MockLLM

    state = {
        "backlog": [
            BacklogItem(
                feature="Add SSO",
                theme="Auth",
                rice_score=12,
                reach=10,
                impact=2,
                confidence=0.9,
                effort=5,
                moscow="Must",
                rationale="Critical",
                source_feedback_ids=["F1"],
            ),
        ],
        "options": {"llm": MockLLM()},
    }
    out = generate_summary(state)
    assert "roadmap_summary" in out["options"]
    summary = out["options"]["roadmap_summary"]
    assert len(summary) > 0
    assert "Roadmap" in summary or "prioris" in summary.lower() or "Démonstration" in summary
