"""Tests import Canny → FeedbackItem[]."""

from unittest.mock import patch

import pytest

from po_agent.domain.models import FeedbackItem
from po_agent.ingestion.canny_loader import _canny_post_to_feedback, load_from_canny


def test_canny_post_to_feedback():
    post = {
        "id": "abc123",
        "details": "We need SSO with Azure AD.",
        "title": "SSO request",
        "created": "2026-02-15T10:00:00.000Z",
        "author": {"name": "John", "email": "john@acme.com"},
        "category": {"name": "Security"},
        "board": {"name": "Feature Requests"},
    }
    fb = _canny_post_to_feedback(post)
    assert isinstance(fb, FeedbackItem)
    assert fb.id == "canny-abc123"
    assert fb.source == "ticket"
    assert fb.text == "We need SSO with Azure AD."
    assert fb.client == "John"
    assert fb.segment == "Security"
    assert fb.plan == "Feature Requests"
    assert fb.created_at == "2026-02-15"


def test_canny_post_fallback_title():
    post = {"id": "x", "title": "Fallback title", "board": {}}
    fb = _canny_post_to_feedback(post)
    assert fb.text == "Fallback title"


@patch("po_agent.ingestion.canny_loader.requests.Session")
def test_load_from_canny_success(mock_session):
    mock_resp = mock_session.return_value.post.return_value
    mock_resp.raise_for_status = lambda: None
    mock_resp.json.return_value = {
        "hasMore": False,
        "posts": [
            {
                "id": "p1",
                "details": "Feature A",
                "created": "2026-02-01T00:00:00Z",
                "author": {"name": "Alice"},
                "board": {"name": "Board1"},
            },
        ],
    }

    items = load_from_canny(api_key="test-key", limit=10)
    assert len(items) == 1
    assert items[0].id == "canny-p1"
    assert items[0].text == "Feature A"


def test_load_from_canny_no_api_key():
    with pytest.raises(ValueError, match="CANNY_API_KEY"):
        load_from_canny(api_key="")
    with pytest.raises(ValueError, match="CANNY_API_KEY"):
        load_from_canny(api_key="   ")
