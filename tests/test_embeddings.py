"""Tests embeddings (sans appel API)."""

import pytest

from po_agent.intelligence.embeddings import cosine_similarity


def test_cosine_similarity():
    assert cosine_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)
    assert abs(cosine_similarity([1, 0, 0], [0, 1, 0])) < 0.01
    assert cosine_similarity([1, 1, 1], [1, 1, 1]) == pytest.approx(1.0)
