"""Client LLM OpenAI-compatible + interface injectable."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Protocol, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
log = logging.getLogger("po_agent.llm.client")

MAX_RETRIES_429 = 3
RETRY_BACKOFF_BASE = 2.0


class LLM(Protocol):
    """Interface pour tout client LLM."""

    def complete_structured(self, *, system: str, user: str, model: Type[T]) -> T: ...


def _extract_json_content(content: str) -> str:
    """Extrait le JSON si entouré de ```json ... ```."""
    content = (content or "").strip()
    if "```" in content:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if m:
            return m.group(1).strip()
    return content


def _parse_structured(content: str, model: Type[T]) -> T:
    """Parse JSON en modèle Pydantic, avec réparation si malformé (LLM)."""
    try:
        return model.model_validate_json(content)
    except Exception as e:
        try:
            from json_repair import repair_json

            repaired = repair_json(content)
            return model.model_validate_json(repaired)
        except Exception as repair_err:
            log.debug("JSON repair failed: %s", repair_err)
            raise repair_err from e


@dataclass
class OpenAIChatLLM:
    """
    Client LLM OpenAI-compatible (Groq).
    Retry automatique sur 429 (rate limit).
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
        last_err = None
        for attempt in range(MAX_RETRIES_429 + 1):
            try:
                resp = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.2,
                )
                content = resp.choices[0].message.content or ""
                content = _extract_json_content(content)
                return _parse_structured(content, model)
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                if "429" in err_str or "rate" in err_str or "rate_limit" in err_str:
                    if attempt < MAX_RETRIES_429:
                        wait = RETRY_BACKOFF_BASE ** (attempt + 1)
                        log.warning(
                            "Rate limit 429, retry %d/%d in %.1fs: %s",
                            attempt + 1,
                            MAX_RETRIES_429,
                            wait,
                            e,
                        )
                        time.sleep(wait)
                        continue
                raise
        raise last_err


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
