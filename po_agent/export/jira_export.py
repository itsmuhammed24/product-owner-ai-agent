"""Export UserStory[] → CSV Jira (Summary, Description, AC, Story Points)."""

import csv
import io
from typing import List

from po_agent.domain.models import UserStory


def _write_csv(writer: csv.writer, stories: List[UserStory]) -> None:
    writer.writerow(["Summary", "Description", "Acceptance Criteria", "Story Points"])
    for s in stories:
        writer.writerow(
            [
                s.title,
                s.user_story,
                "\n".join(s.acceptance_criteria) if s.acceptance_criteria else "",
                s.complexity,
            ]
        )


def stories_to_jira_csv_string(stories: List[UserStory]) -> str:
    """Retourne le contenu CSV en string (API export, download)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    _write_csv(writer, stories)
    return buf.getvalue()
