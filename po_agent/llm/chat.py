"""Chat assistant PO — Groq. Contexte backlog/insights pour Q&A."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


def chat_reply(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """Réponse texte sur backlog, insights, stories. Groq requis."""
    from po_agent.core.config import get_settings

    s = get_settings()
    key = (api_key or s.groq_api_key).strip()
    if not key:
        return "L'API Groq n'est pas configurée. Définissez GROQ_API_KEY (https://console.groq.com) pour utiliser le chat."

    from openai import OpenAI

    client = OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
    )
    model_name = (model or s.groq_model).strip()

    system = _build_system_prompt(context)
    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
            temperature=0.3,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "rate" in err_msg or "quota" in err_msg:
            raise RuntimeError("Quota API Groq dépassé. Réessayez dans quelques minutes.") from e
        if "timeout" in err_msg or "timed out" in err_msg:
            raise TimeoutError("Le serveur Groq met trop de temps à répondre. Réessayez.") from e
        raise


def _build_system_prompt(context: Optional[Dict[str, Any]]) -> str:
    base = """Tu es l'assistant PO Agent by Thiga — un outil dédié aux Product Owners.
Réponds en français, de façon concise et orientée action. Évite le ton générique des chatbots.
Ton style : professionnel, direct, avec des recommandations concrètes.

Règles importantes :
- Formules de politesse (salut, ça va, bonjour, etc.) : réponds brièvement et propose ton aide.
- "oui vazy", "oui analyse", "analyse rapide", "regarde mes données" : si tu as du contexte (backlog/insights/stories), fais une synthèse ou une analyse immédiate. Ne demande PAS de coller du texte.
- Quand tu as du contexte : utilise-le pour répondre. Ne redemande pas des infos déjà fournies.
- Vérifie les faits : si tu cites RICE/MoSCoW, utilise exactement les données du contexte (pas d'invention)."""
    if context:
        ctx_text = _format_context(context)
        base += f"""

CONTEXTE (données récentes de l'utilisateur) :
{ctx_text}

Utilise ce contexte pour toutes les questions. Exemples :
- "analyse rapide" / "synthèse" → donne une synthèse des priorités et des recommandations
- "mes données" / "feedback important" → analyse le backlog/insights ci-dessus
- "priorisation RICE" → explique en te basant sur les scores réels du contexte
"""
    else:
        base += """

Sans contexte : 
- "Comment démarrer" / "Qu'est-ce que le PO Agent" : explique brièvement : charger des feedbacks (JSONL/CSV) sur la page Feedback, lancer l'analyse, explorer Roadmap et User Stories. Invite à faire une démo ou charger l'exemple.
- Si l'utilisateur colle du feedback client : analyse-le (catégorie, points clés, actions PO).
- Sinon : réponds de façon utile et concise.
"""
    return base


def _format_context(ctx: Dict[str, Any]) -> str:
    parts = []
    if backlog := ctx.get("backlog"):
        parts.append("BACKLOG (priorisé RICE/MoSCoW) :")
        for i, b in enumerate(backlog[:15], 1):
            rice = b.get("rice_score", 0)
            wsjf = b.get("wsjf_score", 0)
            rice_str = f"{rice:.2f}" if isinstance(rice, (int, float)) else str(rice)
            wsjf_str = f"{wsjf:.2f}" if isinstance(wsjf, (int, float)) else str(wsjf)
            parts.append(
                f"  {i}. {b.get('feature', '')} — RICE: {rice_str}, WSJF: {wsjf_str}, MoSCoW: {b.get('moscow', '')}"
            )
            if r := b.get("rationale"):
                parts.append(f"     Justification: {r[:150]}...")
    if insights := ctx.get("insights"):
        parts.append("\nINSIGHTS :")
        for ins in insights[:8]:
            parts.append(f"  - {ins.get('request', '')} ({ins.get('occurrences', 0)} occ.)")
    if stories := ctx.get("stories"):
        parts.append("\nUSER STORIES :")
        for s in stories[:6]:
            parts.append(f"  - {s.get('title', '')} ({s.get('complexity', '')})")
    return "\n".join(parts) if parts else "(contexte vide)"
