"""Tests compatibilité service API — contrat et schéma stables."""

import json

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


# Schéma attendu pour /run (compatibilité avec les consommateurs)
RUN_RESPONSE_KEYS = {"insights", "backlog", "roadmap", "stories", "summary", "errors"}
ROADMAP_KEYS = {"Now", "Next", "Later"}
INSIGHT_KEYS = {"theme", "request", "category", "occurrences", "source_feedback_ids"}
BACKLOG_KEYS = {
    "feature",
    "theme",
    "rice_score",
    "reach",
    "impact",
    "confidence",
    "effort",
    "moscow",
    "rationale",
}
STORY_KEYS = {"title", "user_story", "acceptance_criteria", "complexity"}


@pytest.mark.api
def test_run_response_schema():
    """Le contrat /run doit rester stable : mêmes clés."""
    feedback = [
        {"id": "FB-001", "source": "ticket", "text": "Need SSO with Azure AD."},
        {"id": "FB-002", "source": "email", "text": "Add SCIM provisioning."},
    ]
    r = client.post("/run", json={"feedback": feedback})
    assert r.status_code == 200, r.text
    data = r.json()
    assert RUN_RESPONSE_KEYS.issubset(data.keys()), (
        f"Missing keys: {RUN_RESPONSE_KEYS - data.keys()}"
    )


@pytest.mark.api
def test_run_roadmap_structure():
    """Roadmap doit avoir Now, Next, Later."""
    r = client.post(
        "/run", json={"feedback": [{"id": "FB-001", "source": "ticket", "text": "Need SSO."}]}
    )
    assert r.status_code == 200
    roadmap = r.json().get("roadmap", {})
    assert ROADMAP_KEYS.issubset(roadmap.keys())
    for k in ROADMAP_KEYS:
        assert isinstance(roadmap[k], list)


@pytest.mark.api
def test_run_insights_structure():
    """Insights doivent avoir theme, request, category, etc."""
    r = client.post(
        "/run", json={"feedback": [{"id": "FB-001", "source": "ticket", "text": "SSO needed."}]}
    )
    assert r.status_code == 200
    insights = r.json().get("insights", [])
    for item in insights:
        assert INSIGHT_KEYS.issubset(item.keys()), f"Insight missing keys: {item}"


@pytest.mark.api
def test_run_backlog_structure():
    """Backlog items doivent avoir feature, rice_score, moscow, etc."""
    r = client.post(
        "/run", json={"feedback": [{"id": "FB-001", "source": "ticket", "text": "Need SSO."}]}
    )
    assert r.status_code == 200
    backlog = r.json().get("backlog", [])
    for item in backlog:
        assert BACKLOG_KEYS.issubset(item.keys()), f"Backlog item missing keys: {item}"


@pytest.mark.api
def test_run_stories_structure():
    """Stories doivent avoir title, user_story, acceptance_criteria, complexity (null si échec)."""
    r = client.post(
        "/run", json={"feedback": [{"id": "FB-001", "source": "ticket", "text": "Need SSO."}]}
    )
    assert r.status_code == 200
    stories = r.json().get("stories", [])
    for s in stories:
        if s is None:
            continue
        assert STORY_KEYS.issubset(s.keys()), f"Story missing keys: {s}"


@pytest.mark.api
def test_health_response():
    """/health doit retourner status ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


@pytest.mark.api
def test_ingest_response_schema():
    """/ingest doit retourner feedback et count."""
    content = json.dumps({"id": "FB-001", "source": "ticket", "text": "Need SSO"}) + "\n"
    r = client.post("/ingest", json={"content": content, "format": "jsonl"})
    assert r.status_code == 200
    data = r.json()
    assert "feedback" in data
    assert "count" in data
    assert data["count"] == len(data["feedback"])
