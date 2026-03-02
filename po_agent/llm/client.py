"""Client LLM OpenAI-compatible + interface injectable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    """Interface pour tout client LLM."""

    def complete_structured(self, *, system: str, user: str, model: Type[T]) -> T: ...


@dataclass
class OpenAIChatLLM:
    """
    Client LLM OpenAI-compatible (Groq).
    """

    api_key: str
    model_name: str = "llama-3.1-8b-instant"
    base_url: str | None = None

    def complete_structured(self, *, system: str, user: str, model: Type[T]) -> T:
        from openai import OpenAI

        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        client = OpenAI(**kwargs)
        resp = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or ""
        # Extraire le JSON si entouré de ```json ... ```
        content = content.strip()
        # LLM peut wraper le JSON dans ```json ... ```
        if "```" in content:
            import re

            m = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
            if m:
                content = m.group(1).strip()
        return model.model_validate_json(content)


def build_default_llm() -> LLM:
    """Construit un client LLM Groq à partir des variables d'environnement."""
    from po_agent.core.config import get_settings

    s = get_settings()
    if not s.groq_api_key:
        raise RuntimeError("GROQ_API_KEY requis. Créez une clé sur https://console.groq.com")
    return OpenAIChatLLM(
        api_key=s.groq_api_key,
        model_name=s.groq_model,
        base_url="https://api.groq.com/openai/v1",
    )
