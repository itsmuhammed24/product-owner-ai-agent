"""Loader Canny API → FeedbackItem[]."""

from typing import List, Optional

import requests

from po_agent.domain.models import FeedbackItem


def _canny_post_to_feedback(post: dict, board_name: str = "") -> FeedbackItem:
    """Convertit un post Canny en FeedbackItem."""
    post_id = post.get("id", "unknown")
    board = post.get("board") or {}
    plan = board.get("name") or board_name or None
    details = post.get("details") or post.get("title", "") or ""
    if isinstance(details, str):
        text = details
    else:
        text = str(details)

    created = post.get("created")
    if created:
        created = created[:10] if len(created) >= 10 else created  # YYYY-MM-DD

    author = post.get("author") or post.get("by") or {}
    client = author.get("name") or author.get("email") or None

    category = post.get("category") or {}
    segment = category.get("name") if isinstance(category, dict) else None

    return FeedbackItem(
        id=f"canny-{post_id}",
        source="ticket",
        client=client,
        segment=segment,
        plan=plan,
        created_at=created,
        text=text or "(sans contenu)",
    )


def load_from_canny(
    api_key: str,
    board_id: Optional[str] = None,
    limit: int = 100,
    board_name: str = "",
) -> List[FeedbackItem]:
    """
    Récupère les posts Canny et les convertit en FeedbackItem[].

    Args:
        api_key: Clé API secrète Canny (company settings)
        board_id: ID du board (optionnel, sinon tous les boards)
        limit: Nombre max de posts à récupérer
        board_name: Nom du board pour le champ plan

    Returns:
        Liste de FeedbackItem prêts pour le pipeline

    Raises:
        requests.HTTPError: Si l'API Canny échoue
        ValueError: Si api_key est vide
    """
    if not api_key or not api_key.strip():
        raise ValueError("CANNY_API_KEY requis")

    items: List[FeedbackItem] = []
    skip = 0
    page_limit = min(limit, 100)

    url = "https://canny.io/api/v1/posts/list"
    session = requests.Session()

    while len(items) < limit:
        payload: dict = {
            "apiKey": api_key.strip(),
            "limit": page_limit,
            "skip": skip,
        }
        if board_id:
            payload["boardID"] = board_id

        resp = session.post(url, data=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        posts = data.get("posts") or []
        if not posts:
            break

        for post in posts:
            items.append(_canny_post_to_feedback(post, board_name))
            if len(items) >= limit:
                break

        if not data.get("hasMore", False):
            break

        skip += len(posts)
        if skip >= 500:
            break

    return items[:limit]
