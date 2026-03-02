"""Tests roadmap Now/Next/Later."""

from po_agent.domain.models import BacklogItem
from po_agent.intelligence.roadmap import generate_roadmap


def test_generate_roadmap():
    backlog = [
        BacklogItem(
            feature="SSO",
            theme="auth",
            rice_score=900,
            reach=10,
            impact=2,
            confidence=0.9,
            effort=2,
            moscow="Must",
            rationale="",
            source_feedback_ids=[],
        ),
        BacklogItem(
            feature="Export PDF",
            theme="export",
            rice_score=400,
            reach=5,
            impact=2,
            confidence=0.8,
            effort=2,
            moscow="Should",
            rationale="",
            source_feedback_ids=[],
        ),
        BacklogItem(
            feature="Nice to have",
            theme="other",
            rice_score=100,
            reach=1,
            impact=1,
            confidence=0.5,
            effort=2,
            moscow="Could",
            rationale="",
            source_feedback_ids=[],
        ),
    ]
    roadmap = generate_roadmap(backlog)
    assert len(roadmap["Now"]) == 1
    assert roadmap["Now"][0].feature == "SSO"
    assert len(roadmap["Next"]) == 1
    assert roadmap["Next"][0].feature == "Export PDF"
    assert len(roadmap["Later"]) == 1
    assert roadmap["Later"][0].feature == "Nice to have"
