"""Tests de contrats agents : état entrée/sortie des nœuds LangGraph."""

from po_agent.agents.feedback_agent import analyze_feedback
from po_agent.agents.insight_agent import extract_insights
from po_agent.agents.priority_agent import prioritize_features
from po_agent.agents.story_agent import generate_stories
from po_agent.domain.models import BacklogItem, FeedbackItem, Insight, UserStory
from tests.mock_llm import MockLLM


def test_feedback_agent_contract():
    """FeedbackAgent : feedback[] → options.analyzed_feedback[]"""
    llm = MockLLM()
    state = {
        "feedback": [FeedbackItem(id="F1", source="ticket", text="Add SSO")],
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {"llm": llm},
        "errors": [],
    }
    out = analyze_feedback(state)
    analyzed = out["options"]["analyzed_feedback"]
    assert len(analyzed) == 1
    assert analyzed[0].feedback_id == "F1"


def test_insight_agent_contract():
    """InsightAgent : options.analyzed_feedback → insights[]"""
    from po_agent.domain.models import AnalyzedFeedback

    state = {
        "feedback": [],
        "insights": [],
        "backlog": [],
        "stories": [],
        "options": {
            "analyzed_feedback": [
                AnalyzedFeedback(
                    feedback_id="F1",
                    category="feature_request",
                    summary="SSO",
                    severity=4,
                    extracted_requests=["Add SSO"],
                    evidence_quotes=[],
                ),
            ]
        },
        "errors": [],
    }
    out = extract_insights(state)
    assert "insights" in out
    assert all(isinstance(i, Insight) for i in out["insights"])


def test_priority_agent_contract():
    """PriorityAgent : insights[] → backlog[]"""
    state = {
        "feedback": [],
        "insights": [
            Insight(
                theme="Auth",
                request="add sso",
                category="feature_request",
                occurrences=5,
                evidence_quotes=[],
                source_feedback_ids=["F1"],
            ),
        ],
        "backlog": [],
        "stories": [],
        "options": {},
        "errors": [],
    }
    out = prioritize_features(state)
    assert "backlog" in out
    assert all(isinstance(b, BacklogItem) for b in out["backlog"])


def test_story_agent_contract():
    """StoryAgent : backlog[] → stories[]"""
    state = {
        "feedback": [],
        "insights": [],
        "backlog": [
            BacklogItem(
                feature="Add SSO",
                theme="Auth",
                moscow="Must",
                rice_score=12.0,
                reach=5,
                impact=2.0,
                confidence=0.8,
                effort=4.0,
                source_feedback_ids=["F1"],
                rationale="High demand",
            ),
        ],
        "stories": [],
        "options": {"llm": MockLLM()},
        "errors": [],
    }
    out = generate_stories(state)
    assert "stories" in out
    assert all(s is None or isinstance(s, UserStory) for s in out["stories"])
