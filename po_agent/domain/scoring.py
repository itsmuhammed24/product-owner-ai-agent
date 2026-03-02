"""RICE + MoSCoW — calculs déterministes."""


def compute_rice(reach: int, impact: float, confidence: float, effort: float) -> float:
    """RICE = (Reach × Impact × Confidence) / Effort."""
    if effort == 0:
        return 0
    return (reach * impact * confidence) / effort


def compute_wsjf(cost_of_delay: float, effort: float) -> float:
    """WSJF = Cost of Delay / Job Size (effort)."""
    if effort == 0:
        return 0
    return cost_of_delay / effort


def moscow_from_rice(score: float) -> str:
    """RICE → MoSCoW (seuils absolus, fallback). Utiliser assign_moscow_by_quartiles pour un batch."""
    if score >= 800:
        return "Must"
    elif score >= 400:
        return "Should"
    elif score >= 150:
        return "Could"
    else:
        return "Wont"


def assign_moscow_by_quartiles(backlog: list, score_key: str = "rice_score") -> None:
    """
    Assigne Must/Should/Could/Wont selon les quartiles du batch (top RICE = Must).
    Top 25% = Must, 25% = Should, 25% = Could, 25% = Wont.
    In-place.
    """
    if not backlog:
        return
    n = len(backlog)
    sorted_items = sorted(backlog, key=lambda b: getattr(b, score_key, 0), reverse=True)
    for rank, item in enumerate(sorted_items):
        q = rank / n if n > 0 else 0
        if q < 0.25:
            item.moscow = "Must"
        elif q < 0.5:
            item.moscow = "Should"
        elif q < 0.75:
            item.moscow = "Could"
        else:
            item.moscow = "Wont"
