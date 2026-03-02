"""Tests pipeline end-to-end avec MockLLM."""

from pathlib import Path

from po_agent.ingestion.loader import load_jsonl
from po_agent.pipelines.run import run_full_pipeline
from tests.mock_llm import MockLLM


def test_pipeline_e2e_minimal():
    path = Path(__file__).parent.parent / "data" / "samples" / "feedback_minimal.jsonl"
    if path.exists():
        feedback = load_jsonl(path)
    else:
        path = Path(__file__).parent.parent / "data" / "samples" / "feedback_sample.jsonl"
        feedback = load_jsonl(path)[:3]
    assert len(feedback) >= 1
    llm = MockLLM()
    result = run_full_pipeline(feedback[:3], llm=llm)
    assert "insights" in result and "backlog" in result and "roadmap" in result
    assert "stories" in result and "summary" in result and "errors" in result


def test_pipeline_e2e_with_fixture(sample_feedback, mock_llm):
    result = run_full_pipeline(sample_feedback, llm=mock_llm)
    assert len(result["stories"]) == len(result["backlog"])
    assert result["summary"]


def test_pipeline_empty_feedback(mock_llm):
    result = run_full_pipeline([], llm=mock_llm)
    assert result["insights"] == []
    assert result["backlog"] == []
    assert result["stories"] == []
    assert result["roadmap"]["Now"] == []
