"""Tests scoring RICE et MoSCoW."""

from po_agent.domain.scoring import compute_rice, compute_wsjf, moscow_from_rice


def test_compute_wsjf():
    assert compute_wsjf(cost_of_delay=100, effort=5) == 20.0
    assert compute_wsjf(cost_of_delay=50, effort=0) == 0


def test_compute_rice():
    score = compute_rice(reach=100, impact=2, confidence=0.8, effort=5)
    assert score == 32.0


def test_moscow_mapping():
    assert moscow_from_rice(900) == "Must"
    assert moscow_from_rice(500) == "Should"
    assert moscow_from_rice(200) == "Could"
    assert moscow_from_rice(50) == "Wont"
