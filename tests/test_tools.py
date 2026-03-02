"""Tests for ReAct-style tools (intent detection)."""

from po_agent.intelligence.tools import detect_tool_intent, execute_tool


def test_detect_whatif_intent():
    tool = detect_tool_intent("Ouvre What-if pour simuler", None)
    assert tool is not None
    assert tool.name == "navigate_whatif"


def test_detect_roadmap_intent():
    tool = detect_tool_intent("Montre la roadmap", None)
    assert tool is not None
    assert tool.name == "navigate_roadmap"


def test_detect_explainability_intent():
    tool = detect_tool_intent("Explique le score RICE de cette feature", None)
    assert tool is not None
    assert tool.name == "navigate_explainability"


def test_detect_search_intent():
    tool = detect_tool_intent("Cherche SSO dans le backlog", None)
    assert tool is not None
    assert tool.name == "search_backlog"


def test_no_intent():
    tool = detect_tool_intent("Bonjour", None)
    assert tool is None


def test_execute_search_tool():
    ctx = {"backlog": [{"feature": "SSO", "theme": "Auth", "rice_score": 50}]}
    out = execute_tool("search_backlog", {"query": "sso"}, ctx)
    assert out["type"] == "search_result"
    assert len(out["matches"]) == 1
    assert out["matches"][0]["feature"] == "SSO"
