"""CritiqueAgent : Reasoning Loop — critique et affine les user stories."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from po_agent.domain.models import BacklogItem, CritiqueBatchOutput, CritiqueItem, UserStory
from po_agent.llm.client import LLM
from po_agent.llm.prompts import (
    CRITIQUE_AGENT_SYSTEM,
    CRITIQUE_AGENT_USER,
    STORY_AGENT_SYSTEM,
    build_story_refinement_prompt,
)

log = logging.getLogger("po_agent.critique_agent")

SCORE_THRESHOLD = 4  # En dessous, on régénère


def _critique_batch(
    llm: LLM,
    valid_pairs: List[tuple[int, BacklogItem, UserStory]],
) -> Dict[int, CritiqueItem] | None:
    """Critique les stories. valid_pairs = [(backlog_idx, item, story), ...]. None si échec."""
    if not valid_pairs:
        return {}
    try:
        payload = [
            {
                "feature": bl.feature,
                "title": s.title,
                "user_story": s.user_story,
                "acceptance_criteria": s.acceptance_criteria[:3],
            }
            for _, bl, s in valid_pairs
        ]
        user_prompt = CRITIQUE_AGENT_USER.format(stories_json=json.dumps(payload, indent=2))
        out = llm.complete_structured(
            system=CRITIQUE_AGENT_SYSTEM,
            user=user_prompt,
            model=CritiqueBatchOutput,
        )
        items = out.items if hasattr(out, "items") else []
        return {valid_pairs[j][0]: it for j, it in enumerate(items) if j < len(valid_pairs)}
    except Exception as e:
        log.warning("Critique batch failed: %s", e)
        return None


def _refine_story(
    llm: LLM,
    item: BacklogItem,
    original: UserStory,
    hint: str,
    product_name: str = "",
    target_segment: str = "",
) -> UserStory | None:
    """Régénère une story avec le hint d'amélioration."""
    try:
        user_prompt = build_story_refinement_prompt(
            item.feature,
            item.theme,
            item.moscow,
            item.rice_score,
            original.title,
            original.user_story,
            original.acceptance_criteria,
            hint,
            product_name,
            target_segment,
        )
        return llm.complete_structured(
            system=STORY_AGENT_SYSTEM,
            user=user_prompt,
            model=UserStory,
        )
    except Exception as e:
        log.warning("Refinement failed for %s: %s", item.feature[:30], e)
        return None


def critique_and_refine_stories(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Critique les stories, régénère celles avec score < 4.
    Reasoning Loop : générer → critiquer → raffiner si nécessaire.
    """
    stories_raw = state.get("stories", [])
    backlog: List[BacklogItem] = state.get("backlog", [])
    llm = state.get("options", {}).get("llm")
    opts = state.get("options", {})

    # Sauvegarde pour diff avant/après (UI) — garde l'alignement par index
    if stories_raw and "stories_before_critique" not in opts:
        opts["stories_before_critique"] = [
            (
                s.model_dump()
                if hasattr(s, "model_dump")
                else (s.copy() if isinstance(s, dict) else s)
            )
            if s is not None
            else None
            for s in stories_raw
        ]
    product_name = opts.get("product_name", "") or ""
    target_segment = opts.get("target_segment", "") or ""

    # stories peut contenir None (échecs). Aligné avec backlog par index.
    valid_pairs = [
        (i, backlog[i], stories_raw[i])
        for i in range(min(len(backlog), len(stories_raw)))
        if i < len(stories_raw) and stories_raw[i] is not None
    ]

    if not valid_pairs or not llm:
        return state
    critiques = _critique_batch(llm, valid_pairs)
    if not critiques:
        return state

    refined_count = 0
    for idx, item, story in valid_pairs:
        crit = critiques.get(idx)
        if not crit or crit.score >= SCORE_THRESHOLD:
            continue
        hint = crit.improvement_hint or "Improve clarity and testability."
        refined = _refine_story(llm, item, story, hint, product_name, target_segment)
        if refined:
            stories_raw[idx] = refined
            refined_count += 1

    if refined_count:
        log.info(
            "CritiqueAgent: refined %d stories (pass %d)",
            refined_count,
            opts.get("critique_pass", 0) + 1,
        )
        state["stories"] = stories_raw

    opts["critique_refined_count"] = refined_count
    opts["critique_pass"] = opts.get("critique_pass", 0) + 1
    return state
