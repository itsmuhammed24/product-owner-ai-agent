"""Tests validation des entrées pipeline."""

from po_agent.core.validation import validate_and_prepare_feedback
from po_agent.domain.models import FeedbackItem


def test_validate_limit_count():
    feedback = [FeedbackItem(id=f"FB-{i}", source="ticket", text="x") for i in range(150)]
    prepared, warnings = validate_and_prepare_feedback(feedback, max_count=100)
    assert len(prepared) == 100
    assert any("Limite" in w for w in warnings)


def test_validate_truncate_text():
    long_text = "a" * 15_000
    feedback = [FeedbackItem(id="FB-1", source="ticket", text=long_text)]
    prepared, warnings = validate_and_prepare_feedback(feedback, max_text_length=5000)
    assert len(prepared[0].text) <= 5015
    assert "[tronqué]" in prepared[0].text
    assert any("tronqué" in w for w in warnings)


def test_validate_ok():
    feedback = [
        FeedbackItem(id="FB-1", source="ticket", text="Short"),
        FeedbackItem(id="FB-2", source="email", text="Normal length"),
    ]
    prepared, warnings = validate_and_prepare_feedback(feedback)
    assert len(prepared) == 2
    assert prepared[0].text == "Short"
    assert len(warnings) == 0
