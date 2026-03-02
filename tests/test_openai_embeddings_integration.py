"""Test d'intégration embeddings OpenAI — nécessite OPENAI_API_KEY dans .env."""

import os

import pytest

# Charger .env avant le test
pytest.importorskip("dotenv")
from dotenv import load_dotenv

load_dotenv()

from po_agent.intelligence.embeddings import cluster_requests, embeddings_available


@pytest.mark.skipif(
    not embeddings_available(),
    reason="OPENAI_API_KEY non défini — définir dans .env pour exécuter",
)
def test_openai_cluster_requests():
    """Vérifie que cluster_requests appelle l'API OpenAI et regroupe les requêtes similaires."""
    requests = [
        "Add SSO authentication",
        "Support SAML login",
        "Azure AD integration",
    ]
    clusters = cluster_requests(requests, threshold=0.7)
    assert len(clusters) >= 1
    assert all(isinstance(c, list) and len(c) >= 1 for c in clusters)
    # Toutes les requêtes doivent être présentes (clusterisées ou seules)
    flat = [r for c in clusters for r in c]
    assert set(flat) == set(requests)
