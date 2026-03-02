"""Heuristiques PO simples, déterministes."""


def default_confidence_from_occurrences(occurrences: int) -> float:
    """Confiance par défaut selon le nombre d'occurrences."""
    if occurrences >= 10:
        return 0.9
    elif occurrences >= 5:
        return 0.75
    elif occurrences >= 2:
        return 0.6
    else:
        return 0.5


def default_impact_from_segment(segment: str | None) -> float:
    """Impact par défaut selon le segment client."""
    if segment == "enterprise":
        return 3.0
    elif segment == "mid-market":
        return 2.0
    else:
        return 1.0
