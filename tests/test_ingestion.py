"""Tests ingestion JSONL/CSV → FeedbackItem[] — 100% sans LLM."""

from pathlib import Path

import pytest

from po_agent.ingestion.loader import load_csv, load_jsonl


def test_load_jsonl():
    path = Path("data/samples/feedback_sample.jsonl")
    items = load_jsonl(path)

    assert len(items) > 0
    assert items[0].id.startswith("FB-")
    assert items[0].text is not None


def test_load_jsonl_sample():
    """Charge feedback_sample.jsonl — 30 items."""
    path = Path("data/samples/feedback_sample.jsonl")
    items = load_jsonl(path)
    assert len(items) == 30
    assert items[0].id == "FB-001"
    assert "Azure AD" in items[0].text


def test_load_csv():
    """Charge feedback_sample.csv."""
    path = Path("data/samples/feedback_sample.csv")
    items = load_csv(path)
    assert len(items) == 30
    assert items[0].id == "FB-001"
    assert items[0].client == "Acme"


def test_jsonl_csv_parity():
    """JSONL et CSV contiennent les mêmes ids."""
    jsonl_items = load_jsonl(Path("data/samples/feedback_sample.jsonl"))
    csv_items = load_csv(Path("data/samples/feedback_sample.csv"))
    jsonl_ids = {i.id for i in jsonl_items}
    csv_ids = {i.id for i in csv_items}
    assert jsonl_ids == csv_ids
    assert len(jsonl_ids) == 30


def test_load_minimal_jsonl():
    """Charge feedback_minimal.jsonl — 5 items."""
    path = Path("data/samples/feedback_minimal.jsonl")
    if not path.exists():
        pytest.skip("feedback_minimal.jsonl non trouvé")
    items = load_jsonl(path)
    assert len(items) == 5
    assert items[0].id == "FB-M01"


def test_load_minimal_csv():
    """Charge feedback_minimal.csv."""
    path = Path("data/samples/feedback_minimal.csv")
    if not path.exists():
        pytest.skip("feedback_minimal.csv non trouvé")
    items = load_csv(path)
    assert len(items) == 5


def test_minimal_jsonl_csv_parity():
    """Minimal JSONL et CSV ont les mêmes ids."""
    jsonl_p = Path("data/samples/feedback_minimal.jsonl")
    csv_p = Path("data/samples/feedback_minimal.csv")
    if not jsonl_p.exists() or not csv_p.exists():
        pytest.skip("fichiers minimal non trouvés")
    j = {i.id for i in load_jsonl(jsonl_p)}
    c = {i.id for i in load_csv(csv_p)}
    assert j == c


def test_load_jsonl_empty_file():
    """Fichier vide ou lignes vides → liste vide ou skip."""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        f.write("\n\n")
        path = Path(f.name)
    try:
        items = load_jsonl(path)
        assert items == []
    finally:
        path.unlink(missing_ok=True)


def test_load_csv_missing_column_raises():
    """CSV sans colonne id ou text → erreur validation."""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
    ) as f:
        f.write("foo,bar\nx,y\n")
        path = Path(f.name)
    try:
        with pytest.raises(Exception):
            load_csv(path)
    finally:
        path.unlink(missing_ok=True)


def test_load_jsonl_invalid_raises():
    """Ligne JSON invalide → ValueError avec numéro de ligne."""
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        f.write('{"id":"FB-001","source":"ticket","text":"ok"}\n')
        f.write("not valid json\n")
        path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            load_jsonl(path)
        assert "line 2" in str(exc_info.value).lower() or "line 2" in str(exc_info.value)
    finally:
        Path(path).unlink(missing_ok=True)
