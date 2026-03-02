"""Deps API — get_llm (Groq)."""

from po_agent.llm.client import build_default_llm


def get_llm():
    """Groq (GROQ_API_KEY requis)."""
    return build_default_llm()
