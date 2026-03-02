"""StoryAgent : BacklogItem[] → UserStory[] (résilience + parallelisation + RAG)."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from po_agent.domain.models import BacklogItem, UserStory
from po_agent.llm.client import LLM
from po_agent.llm.prompts import STORY_AGENT_SYSTEM, build_story_user_prompt


def _normalize_item(item: Any) -> BacklogItem | None:
    """Normalise dict/str en BacklogItem. Retourne None si invalide."""
    if isinstance(item, BacklogItem):
        return item
    if isinstance(item, dict):
        try:
            return BacklogItem.model_validate(item)
        except Exception as e:
            logging.getLogger(__name__).debug("BacklogItem validation failed: %s", e)
            return None
    if isinstance(item, str):
        return BacklogItem(
            feature=item[:200],
            theme="other",
            rice_score=1.0,
            reach=1,
            impact=1.0,
            confidence=0.5,
            effort=1.0,
            moscow="Could",
            rationale="From raw string",
            source_feedback_ids=[],
        )
    return None


def _generate_one(
    llm: LLM,
    idx: int,
    item: BacklogItem,
    product_name: str = "",
    target_segment: str = "",
    related_features: List[str] | None = None,
) -> tuple[int, BacklogItem, UserStory | None, str | None]:
    """Génère une story. Retourne (idx, item, story, error)."""
    try:
        user_prompt = build_story_user_prompt(
            item.feature,
            item.theme,
            item.moscow,
            item.rice_score,
            product_name,
            target_segment,
            related_features=related_features,
        )
        story = llm.complete_structured(
            system=STORY_AGENT_SYSTEM,
            user=user_prompt,
            model=UserStory,
        )
        return (idx, item, story, None)
    except Exception as e:
        logging.getLogger(__name__).warning(
            "Story generation failed for %s: %s", item.feature[:50], e
        )
        return (idx, item, None, str(e))


def generate_stories(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node : BacklogItem[] → UserStory[].
    Résilience : erreurs isolées. Parallelisation. RAG : related_features injectés.
    """
    raw_backlog = state.get("backlog", [])
    backlog: List[BacklogItem] = []
    for x in raw_backlog:
        bi = _normalize_item(x)
        if bi:
            backlog.append(bi)

    llm: LLM = state["options"]["llm"]
    opts = state.get("options", {})
    product_name = opts.get("product_name", "") or ""
    target_segment = opts.get("target_segment", "") or ""
    related_map: Dict[int, List[str]] = opts.get("backlog_related_features", {})
    errors: List[str] = state.get("errors", [])

    ordered: List[UserStory | None] = [None] * len(backlog)
    max_workers = min(3, len(backlog)) if backlog else 1  # 3 évite rate limit Groq (6k TPM)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(
                _generate_one,
                llm,
                i,
                item,
                product_name,
                target_segment,
                related_map.get(i),
            ): i
            for i, item in enumerate(backlog)
        }
        for fut in as_completed(futures):
            idx, item, story, err = fut.result()
            if story:
                ordered[idx] = story
            elif err:
                feat = (getattr(item, "feature", None) or str(item))[:30] + "…"
                errors.append(f"Story '{feat}': {err}")

    # Garder l'ordre pour alignement backlog[i] <-> stories[i] (CritiqueAgent)
    state["stories"] = ordered
    state["errors"] = errors
    state["backlog"] = backlog  # normalisé pour CritiqueAgent
    return state
