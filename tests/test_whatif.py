"""Tests What-if simulation."""

from po_agent.intelligence.whatif import recalc_backlog_with_override


def test_recalc_backlog_override_impact():
    backlog = [
        {
            "feature": "Add SSO",
            "theme": "Auth",
            "rice_score": 2.0,
            "reach": 5,
            "impact": 2.0,
            "confidence": 0.8,
            "effort": 4.0,
            "moscow": "Should",
            "rationale": "High demand",
            "source_feedback_ids": ["F1"],
        },
    ]
    out = recalc_backlog_with_override(backlog, 0, impact=3.0)
    assert len(out["backlog"]) == 1
    assert out["backlog"][0]["impact"] == 3.0
    # RICE = (5*3*0.8)/4 = 3.0 > (5*2*0.8)/4 = 2.0
    assert out["backlog"][0]["rice_score"] > backlog[0]["rice_score"]
    assert "roadmap" in out


def test_recalc_invalid_index():
    backlog = [
        {
            "feature": "X",
            "theme": "T",
            "rice_score": 1,
            "reach": 1,
            "impact": 1,
            "confidence": 1,
            "effort": 1,
            "moscow": "Could",
            "rationale": "",
            "source_feedback_ids": [],
        }
    ]
    out = recalc_backlog_with_override(backlog, 99)
    assert len(out["backlog"]) == 1
    assert out["backlog"][0]["feature"] == "X"
