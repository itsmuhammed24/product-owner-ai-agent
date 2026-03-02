"""Tests API complets (run, ingest, stream, canny)."""

import json

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Product Owner" in r.json()["message"]


def test_ingest_jsonl():
    content = json.dumps({"id": "FB-001", "source": "ticket", "text": "Need SSO"}) + "\n"
    r = client.post("/ingest", json={"content": content, "format": "jsonl"})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["feedback"][0]["id"] == "FB-001"
    assert data["feedback"][0]["text"] == "Need SSO"


def test_ingest_csv():
    content = 'id,source,client,segment,plan,created_at,text\nFB-C01,ticket,Acme,mid-market,Pro,2026-02-12,"Need SSO"\n'
    r = client.post("/ingest", json={"content": content, "format": "csv"})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["feedback"][0]["id"] == "FB-C01"


def test_ingest_multiple():
    lines = [
        json.dumps({"id": "FB-1", "source": "ticket", "text": "A"}) + "\n",
        json.dumps({"id": "FB-2", "source": "email", "text": "B"}) + "\n",
    ]
    r = client.post("/ingest", json={"content": "".join(lines), "format": "jsonl"})
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_run_pipeline():
    feedback = [
        {"id": "FB-001", "source": "ticket", "text": "Need SSO with Azure AD."},
        {"id": "FB-002", "source": "email", "text": "Add SCIM provisioning."},
    ]
    r = client.post("/run", json={"feedback": feedback})
    assert r.status_code == 200
    data = r.json()
    assert "insights" in data
    assert "backlog" in data
    assert "roadmap" in data
    assert "stories" in data
    assert "summary" in data
    assert "errors" in data


def test_run_pipeline_too_many_feedbacks():
    """Trop de feedbacks → 400."""
    feedback = [{"id": f"FB-{i}", "source": "ticket", "text": "x"} for i in range(150)]
    r = client.post("/run", json={"feedback": feedback})
    assert r.status_code == 400
    assert "max" in r.json()["detail"].lower() or "limite" in r.json()["detail"].lower()


def test_run_pipeline_empty():
    r = client.post("/run", json={"feedback": []})
    assert r.status_code == 200
    data = r.json()
    assert data["insights"] == []
    assert data["backlog"] == []
    assert data["stories"] == []


def test_ingest_canny_no_key():
    """Canny sans API key → 503."""
    r = client.post("/ingest/canny", json={})
    assert r.status_code == 503
    assert "CANNY" in r.json()["detail"].upper() or "configuré" in r.json()["detail"].lower()


def test_run_stream():
    """Stream retourne des events SSE."""
    feedback = [{"id": "FB-001", "source": "ticket", "text": "Need SSO."}]
    with client.stream("POST", "/run/stream", json={"feedback": feedback}) as r:
        assert r.status_code == 200
        assert "text/event-stream" in r.headers.get("content-type", "")
        chunks = list(r.iter_lines())
    assert len(chunks) > 0
    data_lines = [
        c for c in chunks if (c if isinstance(c, str) else c.decode()).startswith("data: ")
    ]
    assert len(data_lines) >= 1
    last = data_lines[-1] if isinstance(data_lines[-1], str) else data_lines[-1].decode()
    obj = json.loads(last[6:])
    assert "step" in obj


def test_run_partial():
    """Pipeline partiel — stop après insights."""
    feedback = [{"id": "FB-001", "source": "ticket", "text": "Need SSO."}]
    r = client.post("/run/partial", json={"feedback": feedback, "stop_at": "insights"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("partial") is True
    assert "insights" in data
    assert "errors" in data


def test_run_partial_backlog():
    """Pipeline partiel — stop après backlog."""
    feedback = [
        {"id": "FB-001", "source": "ticket", "text": "Need SSO."},
        {"id": "FB-002", "source": "email", "text": "Add SCIM."},
    ]
    r = client.post("/run/partial", json={"feedback": feedback, "stop_at": "backlog"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("partial") is True
    assert "backlog" in data


def test_chat():
    r = client.post("/chat", json={"message": "Qu'est-ce que RICE ?"})
    assert r.status_code == 200
    assert "reply" in r.json()
