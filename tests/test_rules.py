"""Tests des règles PO."""

from po_agent.domain.rules import default_confidence_from_occurrences, default_impact_from_segment


def test_default_confidence_from_occurrences():
    assert default_confidence_from_occurrences(12) == 0.9
    assert default_confidence_from_occurrences(5) == 0.75
    assert default_confidence_from_occurrences(2) == 0.6
    assert default_confidence_from_occurrences(1) == 0.5


def test_default_impact_from_segment():
    assert default_impact_from_segment("enterprise") == 3.0
    assert default_impact_from_segment("mid-market") == 2.0
    assert default_impact_from_segment("smb") == 1.0
    assert default_impact_from_segment(None) == 1.0
