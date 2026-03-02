"""Modèles domaine — FeedbackItem, Insight, BacklogItem, UserStory."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

FeedbackCategory = Literal[
    "bug",
    "feature_request",
    "ux_pain",
    "performance",
    "pricing",
    "compliance",
    "other",
]

Moscow = Literal["Must", "Should", "Could", "Wont"]
Complexity = Literal["XS", "S", "M", "L", "XL"]


class AnalyzedFeedback(BaseModel):
    feedback_id: str
    category: FeedbackCategory
    summary: str = Field(..., description="One-sentence summary of the feedback.")  # noqa: E501
    severity: int = Field(..., ge=1, le=5, description="How painful/urgent it is.")
    extracted_requests: List[str] = Field(
        default_factory=list,
        description="Feature requests or improvements.",
    )
    evidence_quotes: List[str] = Field(
        default_factory=list,
        description="Short verbatim snippets.",
    )


class FeedbackItem(BaseModel):
    id: str
    source: Literal["email", "ticket", "comment"]
    client: Optional[str] = None
    segment: Optional[str] = None
    plan: Optional[str] = None
    created_at: Optional[str] = None
    text: str


class Insight(BaseModel):
    theme: str
    request: str
    category: FeedbackCategory
    occurrences: int
    evidence_quotes: List[str]
    source_feedback_ids: List[str]


class BacklogItem(BaseModel):
    feature: str
    theme: str
    rice_score: float
    reach: int
    impact: float
    confidence: float
    effort: float
    moscow: Moscow
    rationale: str
    source_feedback_ids: List[str]
    wsjf_score: float = 0.0
    cost_of_delay: float = 0.0


def _norm_acceptance_criterion(item: object) -> str:
    """Normalise un critère : str OK, dict given/when/then → string."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        parts = []
        for key in ("given", "when", "then"):
            if key in item and item[key]:
                parts.append(f"{key.capitalize()} {item[key]}".strip())
        if parts:
            return ". ".join(parts)
        return str(item)
    return str(item)


class UserStory(BaseModel):
    title: str
    user_story: str
    acceptance_criteria: List[str]
    complexity: Complexity

    @field_validator("acceptance_criteria", mode="before")
    @classmethod
    def normalize_acceptance_criteria(cls, v: object) -> List[str]:
        """LLM peut retourner [{"given":"...","when":"...","then":"..."}] → convertir en strings."""
        if not isinstance(v, list):
            return []
        return [_norm_acceptance_criterion(x) for x in v]


class PrioritySuggestion(BaseModel):
    """Suggestion LLM pour un insight (impact, effort, rationale)."""

    impact: float = Field(ge=1.0, le=3.0, description="Business impact 1-3")
    effort: float = Field(ge=1.0, le=10.0, description="Effort estimate 1-10")
    rationale: str = Field(..., description="Brief business justification")


class PriorityBatchOutput(BaseModel):
    """Sortie batch du PriorityAgent LLM."""

    items: List[PrioritySuggestion]


class AnalyzedFeedbackBatch(BaseModel):
    """Sortie batch FeedbackAgent."""

    items: List[AnalyzedFeedback]


class RoadmapSummary(BaseModel):
    """Synthèse exécutive de la roadmap."""

    summary: str = Field(..., description="3-5 sentence executive summary")


class CritiqueItem(BaseModel):
    """Critique d'une user story (LLM-as-a-judge)."""

    score: int = Field(..., ge=1, le=5, description="Quality 1-5")
    improvement_hint: str | None = Field(
        default=None, description="Suggestion d'amélioration si score < 4"
    )


class CritiqueBatchOutput(BaseModel):
    """Sortie batch CritiqueAgent."""

    items: List[CritiqueItem]
