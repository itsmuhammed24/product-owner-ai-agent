"""Tests Chroma vector store (nécessite pip install -e ".[chroma]")."""

import pytest

try:
    import chromadb  # noqa: F401

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


@pytest.mark.skipif(
    not CHROMA_AVAILABLE, reason='chromadb non installé (pip install -e ".[chroma]")'
)
def test_chroma_available():
    """Chroma doit être importable si [chroma] installé."""
    from po_agent.intelligence.vector_store import _chroma_available

    assert _chroma_available()


@pytest.mark.skipif(not CHROMA_AVAILABLE, reason="chromadb non installé")
def test_add_and_query_chroma(tmp_path, monkeypatch):
    """Ajout et requête Chroma (isolé avec tmp_path)."""
    from po_agent.intelligence.vector_store import add_to_store, query_similar

    monkeypatch.setenv("USE_CHROMA", "true")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("SENTENCE_TRANSFORMERS_HOME", str(tmp_path / ".cache"))

    add_to_store(["Add SSO", "Calendar view", "Export to PDF"])
    similar = query_similar("Add SSO", top_k=2)
    assert isinstance(similar, list)
    assert len(similar) <= 2
