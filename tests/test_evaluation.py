"""Tests évaluation — métriques qualité, non-régression (LLMOps)."""

from po_agent.domain.models import UserStory
from po_agent.evaluation.metrics import (
    acceptance_criteria_count_valid,
    complexity_valid,
    compute_story_quality_metrics,
    user_story_format_valid,
)
from po_agent.pipelines.run import run_full_pipeline


class TestUserStoryFormat:
    """Validation du format user story."""

    def test_valid_format(self):
        assert user_story_format_valid("As a admin, I want SSO, so that users can sign in.")
        assert user_story_format_valid("As a user, I want export PDF, so that I can share reports.")

    def test_invalid_format(self):
        assert not user_story_format_valid("")
        assert not user_story_format_valid("I want SSO")
        assert not user_story_format_valid("As a admin, I need SSO")  # pas "I want"
        assert not user_story_format_valid("As a admin, I want SSO")  # pas "so that"


class TestAcceptanceCriteria:
    def test_valid_count(self):
        assert acceptance_criteria_count_valid(4)
        assert acceptance_criteria_count_valid(7)
        assert not acceptance_criteria_count_valid(3)
        assert not acceptance_criteria_count_valid(8)


class TestComplexity:
    def test_valid_complexity(self):
        for c in ("XS", "S", "M", "L", "XL"):
            assert complexity_valid(c)
        assert not complexity_valid("XXL")
        assert not complexity_valid("")


class TestComputeStoryQualityMetrics:
    """Métriques agrégées."""

    def test_empty_stories(self):
        m = compute_story_quality_metrics([])
        assert m.total == 0
        assert m.overall_score == 0.0

    def test_valid_stories(self):
        stories = [
            UserStory(
                title="SSO",
                user_story="As a admin, I want SSO, so that users sign in.",
                acceptance_criteria=["Given A", "When B", "Then C", "Given D"],
                complexity="M",
            ),
        ]
        m = compute_story_quality_metrics(stories)
        assert m.total == 1
        assert m.valid_format == 1
        assert m.valid_criteria_count == 1
        assert m.valid_complexity == 1
        assert m.overall_score == 1.0

    def test_mixed_quality(self):
        stories = [
            UserStory(
                title="A",
                user_story="As a x, I want y, so that z.",
                acceptance_criteria=["a"] * 4,
                complexity="S",
            ),
            UserStory(
                title="B",
                user_story="Invalid format",
                acceptance_criteria=["b"] * 5,
                complexity="L",
            ),
        ]
        m = compute_story_quality_metrics(stories)
        assert m.total == 2
        assert m.valid_format == 1
        assert m.valid_complexity == 2
        assert m.overall_score < 1.0


class TestPipelineNonRegression:
    """Non-régression : le pipeline doit produire des stories de qualité acceptable."""

    def test_mock_llm_produces_valid_format(self, sample_feedback, mock_llm):
        """MockLLM doit produire des stories au format valide."""
        result = run_full_pipeline(sample_feedback, llm=mock_llm)
        stories = result.get("stories", [])
        assert len(stories) >= 1
        m = compute_story_quality_metrics(stories)
        assert m.overall_score >= 0.5, f"Quality too low: {m}"

    def test_stories_count_matches_backlog(self, sample_feedback, mock_llm):
        """Le nombre de stories doit correspondre au backlog."""
        result = run_full_pipeline(sample_feedback, llm=mock_llm)
        assert len(result["stories"]) == len(result["backlog"])
