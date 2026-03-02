"""Métriques de qualité pour user stories (format, critères, complexité)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

VALID_COMPLEXITY = {"XS", "S", "M", "L", "XL"}
MIN_ACCEPTANCE_CRITERIA = 4
MAX_ACCEPTANCE_CRITERIA = 7


def user_story_format_valid(user_story: str) -> bool:
    """
    Vérifie le format As a / I want / So that.
    """
    if not user_story or not isinstance(user_story, str):
        return False
    s = user_story.strip().lower()
    if not s.startswith("as a "):
        return False
    if "i want" not in s:
        return False
    if "so that" not in s:
        return False
    return True


def acceptance_criteria_count_valid(count: int) -> bool:
    """4 à 7 critères d'acceptation (spec)."""
    return MIN_ACCEPTANCE_CRITERIA <= count <= MAX_ACCEPTANCE_CRITERIA


def complexity_valid(complexity: str) -> bool:
    """Complexité dans XS, S, M, L, XL."""
    return str(complexity).upper() in VALID_COMPLEXITY


@dataclass
class StoryQualityMetrics:
    """Métriques agrégées pour un batch de stories."""

    total: int
    valid_format: int
    valid_criteria_count: int
    valid_complexity: int
    score_format: float  # 0-1
    score_criteria: float
    score_complexity: float
    overall_score: float  # moyenne des 3


def compute_story_quality_metrics(stories: List[Any]) -> StoryQualityMetrics:
    """
    Calcule les métriques de qualité sur une liste de UserStory (ou dict).
    Utile pour non-régression et LLMOps.
    """
    valid = [s for s in stories if s is not None]
    total = len(valid)
    if total == 0:
        return StoryQualityMetrics(
            total=0,
            valid_format=0,
            valid_criteria_count=0,
            valid_complexity=0,
            score_format=0.0,
            score_criteria=0.0,
            score_complexity=0.0,
            overall_score=0.0,
        )

    def _get(story: Any, key: str, default=None):
        return getattr(story, key, None) or (story.get(key) if isinstance(story, dict) else default)

    valid_format = sum(1 for s in valid if user_story_format_valid(_get(s, "user_story", "")))
    valid_criteria = sum(
        1
        for s in valid
        if acceptance_criteria_count_valid(len(_get(s, "acceptance_criteria") or []))
    )
    valid_complexity = sum(1 for s in valid if complexity_valid(_get(s, "complexity", "")))

    score_format = valid_format / total
    score_criteria = valid_criteria / total
    score_complexity = valid_complexity / total
    overall = (score_format + score_criteria + score_complexity) / 3.0

    return StoryQualityMetrics(
        total=total,
        valid_format=valid_format,
        valid_criteria_count=valid_criteria,
        valid_complexity=valid_complexity,
        score_format=round(score_format, 3),
        score_criteria=round(score_criteria, 3),
        score_complexity=round(score_complexity, 3),
        overall_score=round(overall, 3),
    )
