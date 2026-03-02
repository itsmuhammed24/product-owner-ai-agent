"""Loader JSONL/CSV → FeedbackItem[]."""

import csv
import json
from pathlib import Path
from typing import List

from po_agent.domain.models import FeedbackItem


def load_jsonl(path: str | Path) -> List[FeedbackItem]:
    """Charge un fichier JSONL et retourne une liste de FeedbackItem validés."""
    items = []
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                item = FeedbackItem.model_validate(raw)
                items.append(item)
            except Exception as e:
                raise ValueError(f"Invalid JSONL at line {line_number}: {e}") from e

    return items


def load_csv(path: str | Path) -> List[FeedbackItem]:
    """Charge un fichier CSV et retourne une liste de FeedbackItem validés."""
    items = []
    path = Path(path)

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=1):
            try:
                item = FeedbackItem.model_validate(row)
                items.append(item)
            except Exception as e:
                raise ValueError(f"Invalid CSV at row {row_number}: {e}") from e

    return items
