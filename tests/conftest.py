"""Fixtures partagés pour les tests."""

from pathlib import Path
from unittest.mock import patch

import pytest

from po_agent.domain.models import (
    AnalyzedFeedback,
    BacklogItem,
    FeedbackItem,
    Insight,
)
from tests.mock_llm import MockLLM


@pytest.fixture
def sample_feedback() -> list[FeedbackItem]:
    """5 feedbacks de base pour tests rapides."""
    return [
        FeedbackItem(
            id="FB-001",
            source="ticket",
            text="SSO with Azure AD is mandatory.",
            client="Acme",
            segment="mid-market",
        ),
        FeedbackItem(
            id="FB-002",
            source="email",
            text="Add SCIM provisioning.",
            client="Acme",
            segment="mid-market",
        ),
        FeedbackItem(
            id="FB-003",
            source="comment",
            text="PDF export breaks layout.",
            client="Nova",
            segment="agency",
        ),
        FeedbackItem(
            id="FB-004",
            source="ticket",
            text="We need audit logs for compliance.",
            client="BlueFin",
            segment="enterprise",
        ),
        FeedbackItem(
            id="FB-005",
            source="email",
            text="Subtasks need assignees and due dates.",
            client="BlueFin",
            segment="enterprise",
        ),
    ]


@pytest.fixture
def sample_insights() -> list[Insight]:
    """Insights typiques pour tests."""
    return [
        Insight(
            theme="Auth",
            request="add sso",
            category="feature_request",
            occurrences=5,
            evidence_quotes=["SSO mandatory"],
            source_feedback_ids=["FB-001", "FB-002"],
        ),
        Insight(
            theme="Export",
            request="fix pdf export",
            category="bug",
            occurrences=2,
            evidence_quotes=["PDF breaks"],
            source_feedback_ids=["FB-003"],
        ),
    ]


@pytest.fixture
def sample_backlog() -> list[BacklogItem]:
    """Backlog items pour tests."""
    return [
        BacklogItem(
            feature="Add SSO",
            theme="Auth",
            rice_score=12.0,
            reach=5,
            impact=2.0,
            confidence=0.8,
            effort=4.0,
            moscow="Must",
            rationale="High demand",
            source_feedback_ids=["FB-001"],
        ),
        BacklogItem(
            feature="Fix PDF export",
            theme="Export",
            rice_score=6.0,
            reach=2,
            impact=1.5,
            confidence=0.7,
            effort=2.0,
            moscow="Should",
            rationale="User pain",
            source_feedback_ids=["FB-003"],
        ),
    ]


@pytest.fixture
def sample_analyzed_feedback() -> list[AnalyzedFeedback]:
    """AnalyzedFeedback pour tests InsightAgent."""
    return [
        AnalyzedFeedback(
            feedback_id="FB-001",
            category="feature_request",
            summary="SSO request",
            severity=4,
            extracted_requests=["Add SSO"],
            evidence_quotes=["SSO mandatory"],
        ),
        AnalyzedFeedback(
            feedback_id="FB-002",
            category="feature_request",
            summary="SCIM",
            severity=3,
            extracted_requests=["Add SSO", "SCIM"],
            evidence_quotes=[],
        ),
    ]


@pytest.fixture
def mock_llm():
    """MockLLM pour tests sans appel API."""
    return MockLLM()


@pytest.fixture(autouse=True)
def _patch_llm_for_api_tests():
    """Injecte MockLLM dans l'API pour tous les tests (évite GROQ_API_KEY)."""
    with patch("apps.api.deps.get_llm", return_value=MockLLM()):
        yield


@pytest.fixture(autouse=True)
def _patch_chat_for_api_tests():
    """Mock chat_reply pour /chat (évite appel Groq)."""
    with patch(
        "apps.api.routes.chat_reply",
        return_value="RICE = Reach × Impact × Confidence / Effort. Framework de priorisation.",
    ):
        yield


@pytest.fixture
def sample_jsonl_path() -> Path:
    """Chemin vers feedback_sample.jsonl."""
    return Path("data/samples/feedback_sample.jsonl")


@pytest.fixture
def sample_csv_path() -> Path:
    """Chemin vers feedback_sample.csv."""
    return Path("data/samples/feedback_sample.csv")


@pytest.fixture
def minimal_jsonl_path(tmp_path: Path) -> Path:
    """Crée un JSONL minimal temporaire."""
    p = tmp_path / "minimal.jsonl"
    p.write_text(
        '{"id":"FB-001","source":"ticket","text":"Need SSO"}\n'
        '{"id":"FB-002","source":"email","text":"Add SCIM"}\n',
        encoding="utf-8",
    )
    return p
