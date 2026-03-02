"""Roadmap automatique Now / Next / Later."""

from typing import Dict, List

from po_agent.domain.models import BacklogItem


def generate_roadmap(backlog: List[BacklogItem]) -> Dict[str, List[BacklogItem]]:
    """MoSCoW → Now/Next/Later."""
    roadmap: Dict[str, List[BacklogItem]] = {"Now": [], "Next": [], "Later": []}

    for item in backlog:
        if item.moscow == "Must":
            roadmap["Now"].append(item)
        elif item.moscow == "Should":
            roadmap["Next"].append(item)
        else:
            roadmap["Later"].append(item)

    return roadmap
