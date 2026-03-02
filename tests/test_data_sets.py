"""Tests des jeux de donnees (samples)."""

from pathlib import Path

import pytest

from po_agent.ingestion.loader import load_csv, load_jsonl

SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"


def test_minimal_jsonl_exists():
    """feedback_minimal.jsonl existe et est chargeable."""
    p = SAMPLES_DIR / "feedback_minimal.jsonl"
    assert p.exists()
    items = load_jsonl(p)
    assert len(items) == 6
    assert items[0].id == "FB-M01"
    assert "SSO" in items[0].text


def test_edge_cases_jsonl():
    """feedback_edge_cases.jsonl : champs optionnels, unicode."""
    p = SAMPLES_DIR / "feedback_edge_cases.jsonl"
    if not p.exists():
        pytest.skip("feedback_edge_cases.jsonl non trouve")
    items = load_jsonl(p)
    assert len(items) >= 3
    # Minimal fields
    assert items[0].id == "FB-E01"
    assert items[0].text
    # Unicode
    assert any("café" in i.text or "emoji" in i.text or "日本語" in i.text for i in items)


def test_sample_parity():
    """JSONL et CSV sample ont les memes ids."""
    jsonl_p = SAMPLES_DIR / "feedback_sample.jsonl"
    csv_p = SAMPLES_DIR / "feedback_sample.csv"
    assert jsonl_p.exists()
    assert csv_p.exists()
    jsonl_ids = {i.id for i in load_jsonl(jsonl_p)}
    csv_ids = {i.id for i in load_csv(csv_p)}
    assert jsonl_ids == csv_ids
    assert len(jsonl_ids) == 30


def test_all_samples_valid():
    """Tous les JSONL du dossier samples sont valides."""
    for f in SAMPLES_DIR.glob("*.jsonl"):
        items = load_jsonl(f)
        assert len(items) > 0
        for i in items:
            assert i.id
            assert i.text
            assert i.source in ("email", "ticket", "comment")
