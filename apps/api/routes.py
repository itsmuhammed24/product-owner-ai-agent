"""API REST — health, ingest, run, chat, export."""

import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from po_agent.core.config import MAX_CHAT_MESSAGE_LENGTH
from po_agent.domain.models import FeedbackItem
from po_agent.ingestion.canny_loader import load_from_canny
from po_agent.ingestion.loader import load_csv, load_jsonl
from po_agent.llm.chat import chat_reply
from po_agent.pipelines import run_full_pipeline, run_full_pipeline_stream, run_partial_pipeline

router = APIRouter()


class RunRequest(BaseModel):
    feedback: List[FeedbackItem]


class IngestRequest(BaseModel):
    content: str
    format: str = "jsonl"  # "jsonl" | "csv"


@router.post("/ingest")
def ingest(req: IngestRequest):
    """Parse JSONL/CSV → FeedbackItem[] validés. Limite payload + nb items."""
    from po_agent.core.config import get_settings

    s = get_settings()
    size_mb = len(req.content.encode("utf-8")) / (1024 * 1024)
    if size_mb > s.max_ingest_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Payload trop volumineux (max {s.max_ingest_size_mb} Mo). Réduisez ou augmentez MAX_INGEST_SIZE_MB.",
        )

    suffix = ".csv" if req.format == "csv" else ".jsonl"
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(req.content)
        tmp = f.name
    try:
        if req.format == "csv":
            items = load_csv(tmp)
        else:
            items = load_jsonl(tmp)
        items = items[: s.max_feedbacks]
        return {"feedback": [i.model_dump() for i in items], "count": len(items)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Format invalide : {e}") from e
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


class CannyIngestRequest(BaseModel):
    board_id: Optional[str] = None
    limit: int = 50


@router.post("/ingest/canny")
def ingest_canny(req: CannyIngestRequest = CannyIngestRequest()):
    """
    Importe le feedback depuis Canny (API).
    Nécessite CANNY_API_KEY dans .env.
    """
    from po_agent.core.config import get_settings

    s = get_settings()
    api_key = getattr(s, "canny_api_key", None) or ""
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=503,
            detail="Canny non configuré : définir CANNY_API_KEY dans .env",
        )
    board_id = req.board_id or getattr(s, "canny_board_id", None) or None
    try:
        items = load_from_canny(
            api_key=api_key,
            board_id=board_id,
            limit=min(req.limit, 100),
        )
        return {"feedback": [i.model_dump() for i in items], "count": len(items)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur Canny: {e}") from e


# --- Health ---


@router.get("/health")
def health():
    return {"status": "ok"}


# --- Pipeline ---


@router.post("/run")
def run(req: RunRequest):
    from fastapi.responses import JSONResponse

    from apps.api.deps import get_llm
    from po_agent.core.config import get_settings

    s = get_settings()
    if len(req.feedback) > s.max_feedbacks:
        raise HTTPException(
            status_code=400,
            detail=f"Trop de feedbacks (max {s.max_feedbacks}). Réduisez ou augmentez MAX_FEEDBACKS.",
        )
    try:
        llm = get_llm()
        return run_full_pipeline(req.feedback, llm=llm)
    except Exception as e:
        import os

        content = {"error": str(e)}
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback

            content["traceback"] = traceback.format_exc()
        return JSONResponse(status_code=500, content=content)


@router.post("/run/stream")
def run_stream(req: RunRequest):
    """Pipeline en streaming SSE pour progression temps réel."""
    import json

    from fastapi.responses import StreamingResponse

    from apps.api.deps import get_llm

    def gen():
        try:
            llm = get_llm()
            for step, data in run_full_pipeline_stream(req.feedback, llm=llm):
                yield f"data: {json.dumps({'step': step, **data})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class PartialRunRequest(BaseModel):
    feedback: List[FeedbackItem]
    stop_at: str = "insights"  # "insights" | "backlog"


@router.post("/run/partial")
def run_partial(req: PartialRunRequest):
    """Pipeline partiel — stop après insights ou backlog (human-in-the-loop)."""
    from fastapi.responses import JSONResponse

    from apps.api.deps import get_llm
    from po_agent.core.config import get_settings

    s = get_settings()
    if len(req.feedback) > s.max_feedbacks:
        raise HTTPException(
            status_code=400,
            detail=f"Trop de feedbacks (max {s.max_feedbacks}).",
        )
    if req.stop_at not in ("insights", "backlog"):
        raise HTTPException(status_code=400, detail="stop_at doit être insights ou backlog")
    try:
        llm = get_llm()
        return run_partial_pipeline(req.feedback, llm=llm, stop_at=req.stop_at)
    except Exception as e:
        import os

        content = {"error": str(e)}
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback

            content["traceback"] = traceback.format_exc()
        return JSONResponse(status_code=500, content=content)


class WhatIfRequest(BaseModel):
    backlog: List[Dict[str, Any]]
    item_index: int
    impact: Optional[float] = None
    effort: Optional[float] = None
    reach: Optional[int] = None
    confidence: Optional[float] = None


@router.post("/run/whatif")
def run_whatif(req: WhatIfRequest):
    """What-if : recalcul RICE/roadmap avec paramètres modifiés."""
    from fastapi.responses import JSONResponse

    from po_agent.intelligence.whatif import recalc_backlog_with_override

    if req.item_index < 0 or req.item_index >= len(req.backlog):
        return JSONResponse(
            status_code=400,
            content={
                "error": f"item_index invalide ({req.item_index}). Le backlog a {len(req.backlog)} items (index 0 à {len(req.backlog) - 1}).",
            },
        )
    try:
        return recalc_backlog_with_override(
            req.backlog,
            req.item_index,
            impact=req.impact,
            effort=req.effort,
            reach=req.reach,
            confidence=req.confidence,
        )
    except (ValueError, TypeError) as e:
        return JSONResponse(status_code=422, content={"error": str(e)})
    except Exception as e:
        import logging
        import os

        logging.getLogger("apps.api").warning("What-if error: %s", e, exc_info=True)
        content = {"error": str(e)}
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback

            content["traceback"] = traceback.format_exc()
        return JSONResponse(status_code=500, content=content)


# --- Export ---


class ExportJiraRequest(BaseModel):
    stories: List[Dict[str, Any]]


@router.post("/export/jira")
def export_jira(req: ExportJiraRequest):
    """Exporte les user stories en CSV Jira-ready."""
    from fastapi.responses import PlainTextResponse

    from po_agent.domain.models import UserStory
    from po_agent.export.jira_export import stories_to_jira_csv_string

    try:
        stories = [UserStory.model_validate(s) for s in req.stories]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Stories invalides : {e}") from e
    csv_content = stories_to_jira_csv_string(stories)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jira_import.csv"},
    )


@router.post("/export/azure-devops")
def export_azure_devops(req: ExportJiraRequest):
    """Exporte les user stories en CSV Azure DevOps (Work Item Type, Title, Description, AC)."""
    from fastapi.responses import PlainTextResponse

    from po_agent.domain.models import UserStory
    from po_agent.export.azure_devops_export import stories_to_azure_devops_csv_string

    try:
        stories = [UserStory.model_validate(s) for s in req.stories]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Stories invalides : {e}") from e
    csv_content = stories_to_azure_devops_csv_string(stories)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=azure_devops_import.csv"},
    )


# --- Chat (ReAct tools) ---


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=MAX_CHAT_MESSAGE_LENGTH)
    context: Optional[Dict[str, Any]] = None


@router.post("/chat")
def chat(req: ChatRequest):
    """Chat assistant PO : analyse de texte, explication des résultats, et suggestions d'outils ReAct."""
    from fastapi.responses import JSONResponse

    from po_agent.core.config import get_settings
    from po_agent.intelligence.tools import detect_tool_intent

    s = get_settings()
    try:
        reply = chat_reply(
            req.message,
            context=req.context,
            api_key=s.groq_api_key,
            model=s.groq_model,
        )
    except Exception as e:
        err_str = str(e).lower()
        status = 429 if "quota" in err_str or "429" in err_str else 502
        return JSONResponse(status_code=status, content={"error": str(e)})
    tool = detect_tool_intent(req.message, req.context)
    out = {"reply": reply}
    if tool:
        out["tool_suggestion"] = {"name": tool.name, "params": tool.params, "label": tool.label}
    return out
