"""Tools ReAct — détection intent, suggestions actions (navigate, search, partial)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolInvocation:
    """Représente une action outil suggérée par le chat."""

    name: str
    params: Dict[str, Any]
    label: str


TOOLS = [
    {
        "name": "navigate_whatif",
        "description": "Ouvrir l'onglet What-if pour simuler Impact/Effort sur une feature",
        "keywords": ["what-if", "whatif", "simul", "recalcul", "impact", "effort", "scénario"],
        "params_schema": {},
    },
    {
        "name": "navigate_roadmap",
        "description": "Afficher la roadmap (Now/Next/Later)",
        "keywords": ["roadmap", "priorité", "now", "next", "later", "planning"],
        "params_schema": {},
    },
    {
        "name": "navigate_explainability",
        "description": "Voir les explications RICE/WSJF/MoSCoW par item",
        "keywords": ["expliqu", "justification", "rice", "wsjf", "moscow", "détail", "rationale"],
        "params_schema": {},
    },
    {
        "name": "search_backlog",
        "description": "Chercher une feature dans le backlog",
        "keywords": ["cherche", "trouve", "feature", "où est"],
        "params_schema": {"query": "str"},
    },
    {
        "name": "run_partial_insights",
        "description": "Revue après insights (human-in-the-loop)",
        "keywords": ["revue", "après insights", "stop insights", "partial insights"],
        "params_schema": {},
    },
    {
        "name": "run_partial_backlog",
        "description": "Revue après backlog (human-in-the-loop)",
        "keywords": ["revue backlog", "stop backlog", "partial backlog", "après priorisation"],
        "params_schema": {},
    },
]


def detect_tool_intent(
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> Optional[ToolInvocation]:
    """
    Détecte si le message de l'utilisateur correspond à une action outil.
    Retourne un ToolInvocation si un intent est reconnu.
    """
    msg_lower = message.lower().strip()
    if len(msg_lower) < 3:
        return None

    # Premier outil matchant les keywords (ordre TOOLS)
    for tool in TOOLS:
        if any(kw in msg_lower for kw in tool["keywords"]):
            params: Dict[str, Any] = {}
            if "query" in tool.get("params_schema", {}):
                # Extraire une requête de recherche si présente
                m = re.search(
                    r"(?:cherche|trouve|où)\s+(?:est\s+)?['\"]?([^'\"]+)['\"]?", msg_lower, re.I
                )
                if m:
                    params["query"] = m.group(1).strip()
            label = _tool_label(tool["name"], params)
            return ToolInvocation(name=tool["name"], params=params, label=label)

    return None


def _tool_label(name: str, params: Dict[str, Any]) -> str:
    labels = {
        "navigate_whatif": "Ouvrir What-if simulation",
        "navigate_roadmap": "Voir la Roadmap",
        "navigate_explainability": "Voir les explications",
        "search_backlog": f"Rechercher « {params.get('query', '')} »"
        if params.get("query")
        else "Rechercher dans le backlog",
        "run_partial_insights": "Lancer revue après insights",
        "run_partial_backlog": "Lancer revue après backlog",
    }
    return labels.get(name, name)


def execute_tool(
    name: str,
    params: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Exécute une action outil côté backend (pour les outils qui ne sont pas juste de la navigation).
    Retourne un résultat exploitable par le frontend.
    """
    if name == "search_backlog":
        query = (params.get("query") or "").lower()
        backlog = (context or {}).get("backlog", [])
        matches = [
            b
            for b in backlog
            if query in (b.get("feature") or "").lower() or query in (b.get("theme") or "").lower()
        ]
        return {"type": "search_result", "matches": matches[:5], "query": query}

    if name in ("run_partial_insights", "run_partial_backlog"):
        stop = "insights" if "insights" in name else "backlog"
        return {"type": "partial_suggestion", "stop_at": stop}

    # Navigation tools : le frontend gère
    return {"type": "navigate", "target": name}
