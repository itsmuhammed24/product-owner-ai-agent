"""Mock LLM pour tests unitaires (sans appel API)."""

from po_agent.domain.models import (
    AnalyzedFeedback,
    AnalyzedFeedbackBatch,
    CritiqueBatchOutput,
    CritiqueItem,
    PriorityBatchOutput,
    PrioritySuggestion,
    RoadmapSummary,
    UserStory,
)


class MockLLM:
    """Simule les réponses LLM pour les tests."""

    def complete_structured(self, *, system: str, user: str, model):
        if model is AnalyzedFeedback or model.__name__ == "AnalyzedFeedback":
            return AnalyzedFeedback(
                feedback_id="FB-001",
                category="feature_request",
                summary="Customer requests feature (test).",
                severity=4,
                extracted_requests=["Add requested feature"],
                evidence_quotes=["From feedback text"],
            )
        if model is AnalyzedFeedbackBatch or model.__name__ == "AnalyzedFeedbackBatch":
            items = [
                AnalyzedFeedback(
                    feedback_id="TEMP",
                    category="feature_request",
                    summary="Customer requests (test batch).",
                    severity=4,
                    extracted_requests=["Add requested feature"],
                    evidence_quotes=["From feedback text"],
                )
                for _ in range(5)
            ]
            return AnalyzedFeedbackBatch(items=items)
        if model is PriorityBatchOutput or model.__name__ == "PriorityBatchOutput":
            return PriorityBatchOutput(
                items=[
                    PrioritySuggestion(impact=2.0, effort=4.0, rationale="Prioritized (test).")
                    for _ in range(10)
                ]
            )
        if model is RoadmapSummary or model.__name__ == "RoadmapSummary":
            return RoadmapSummary(summary="Roadmap priorisée (test).")
        if model is CritiqueBatchOutput or model.__name__ == "CritiqueBatchOutput":
            return CritiqueBatchOutput(
                items=[
                    CritiqueItem(score=3, improvement_hint="Add more specific AC."),
                    *[CritiqueItem(score=5, improvement_hint=None) for _ in range(9)],
                ]
            )
        return UserStory(
            title="Add SSO via SAML",
            user_story="As a workspace admin, I want SSO via SAML, so that users can sign in securely.",
            acceptance_criteria=["AC1", "AC2", "AC3", "AC4"],
            complexity="M",
        )
