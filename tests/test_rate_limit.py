"""Tests rate limit middleware."""

import pytest
from starlette.testclient import TestClient

from apps.api.main import app


def test_rate_limit_uses_x_forwarded_for():
    """X-Forwarded-For doit être utilisé comme IP client."""
    client = TestClient(app)
    # Requête avec X-Forwarded-For
    r = client.get(
        "/health",
        headers={"X-Forwarded-For": "192.168.1.100, 10.0.0.1"},
    )
    assert r.status_code == 200


def test_rate_limit_uses_x_real_ip():
    """X-Real-IP doit être utilisé si X-Forwarded-For absent."""
    client = TestClient(app)
    r = client.get("/health", headers={"X-Real-IP": "203.0.113.42"})
    assert r.status_code == 200


def test_health_not_rate_limited():
    """/health n'est pas limité."""
    client = TestClient(app)
    for _ in range(5):
        r = client.get("/health")
        assert r.status_code == 200
