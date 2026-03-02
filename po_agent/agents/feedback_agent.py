"""FeedbackAgent : FeedbackItem[] → AnalyzedFeedback[] (batching optionnel)."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from po_agent.domain.models import AnalyzedFeedback, AnalyzedFeedbackBatch, FeedbackItem
from po_agent.llm.client import LLM
from po_agent.llm.prompts import (
    FEEDBACK_AGENT_SYSTEM,
    FEEDBACK_BATCH_SYSTEM,
    FEEDBACK_BATCH_USER,
    build_feedback_user_prompt,
)

log = logging.getLogger("po_agent.feedback_agent")

BATCH_SIZE = 5  # Plus gros batch = moins d'appels LLM


def _analyze_batch(
    llm: LLM,
    batch: List[FeedbackItem],
    product_name: str = "",
    target_segment: str = "",
) -> List[AnalyzedFeedback]:
    """Analyse un lot de feedbacks en une requête."""
    from po_agent.llm.prompts import _product_context as ctx_fn

    ctx = ctx_fn(product_name, target_segment)
    lines = [f"ID: {fb.id}\nText: {fb.text}" for fb in batch]
    feedbacks_text = "\n\n---\n\n".join(lines)
    user_prompt = FEEDBACK_BATCH_USER.format(
        product_context=ctx,
        feedbacks_text=feedbacks_text,
    )
    out = llm.complete_structured(
        system=FEEDBACK_BATCH_SYSTEM,
        user=user_prompt,
        model=AnalyzedFeedbackBatch,
    )
    items = out.items if hasattr(out, "items") else []
    for i, fb in enumerate(batch):
        if i < len(items):
            items[i].feedback_id = fb.id
    if len(items) >= len(batch):
        return items[: len(batch)]
    # LLM a retourné moins d'items : fallback one-by-one pour les manquants
    result = list(items)
    for i in range(len(items), len(batch)):
        fb = batch[i]
        _, one, err = _analyze_one(llm, fb, product_name, target_segment)
        if one:
            result.append(one)
        elif err:
            log.warning("Fallback one-by-one for %s: %s", fb.id, err)
    return result


def _analyze_one(
    llm: LLM,
    fb: FeedbackItem,
    product_name: str = "",
    target_segment: str = "",
) -> tuple[str, AnalyzedFeedback | None, str | None]:
    """Analyse un feedback. Retourne (fb_id, result, error)."""
    try:
        user_prompt = build_feedback_user_prompt(fb.id, fb.text, product_name, target_segment)
        out = llm.complete_structured(
            system=FEEDBACK_AGENT_SYSTEM,
            user=user_prompt,
            model=AnalyzedFeedback,
        )
        out.feedback_id = fb.id
        return (fb.id, out, None)
    except Exception as e:
        return (fb.id, None, str(e))


def analyze_feedback(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: FeedbackItem[] → AnalyzedFeedback[].
    Batching par 5, batches en parallèle. Fallback one-by-one si échec.
    """
    feedback: List[FeedbackItem] = state["feedback"]
    llm: LLM = state["options"]["llm"]
    opts = state.get("options", {})
    product_name = opts.get("product_name", "") or ""
    target_segment = opts.get("target_segment", "") or ""
    errors: List[str] = state.get("errors", [])
    use_batch = opts.get("use_feedback_batch", True)

    analyzed: List[AnalyzedFeedback] = []

    if use_batch and len(feedback) >= 2:
        batches = [feedback[i : i + BATCH_SIZE] for i in range(0, len(feedback), BATCH_SIZE)]
        max_workers = min(4, len(batches))
        results_by_idx: Dict[int, List[AnalyzedFeedback]] = {}

        def _run_batch(args: tuple[int, List[FeedbackItem]]) -> None:
            idx, batch = args
            try:
                results_by_idx[idx] = _analyze_batch(llm, batch, product_name, target_segment)
            except Exception as e:
                log.warning("Batch failed, fallback one-by-one: %s", e)
                fallback = []
                for fb in batch:
                    _, result, err = _analyze_one(llm, fb, product_name, target_segment)
                    if result:
                        fallback.append(result)
                    elif err:
                        errors.append(f"Feedback {fb.id}: {err}")
                results_by_idx[idx] = fallback

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            list(ex.map(_run_batch, enumerate(batches)))
        for i in range(len(batches)):
            analyzed.extend(results_by_idx.get(i, []))
    else:
        max_workers = min(5, len(feedback)) if feedback else 1
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {
                ex.submit(_analyze_one, llm, fb, product_name, target_segment): fb
                for fb in feedback
            }
            for fut in as_completed(futures):
                fb_id, result, err = fut.result()
                if result:
                    analyzed.append(result)
                elif err:
                    errors.append(f"Feedback {fb_id}: {err}")

    state["options"]["analyzed_feedback"] = analyzed
    state["errors"] = errors
    return state
