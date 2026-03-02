"""Tests export Jira CSV."""

from po_agent.domain.models import UserStory
from po_agent.export.jira_export import stories_to_jira_csv_string


def test_stories_to_jira_csv_string():
    stories = [
        UserStory(
            title="Add SSO",
            user_story="As admin I want SSO",
            acceptance_criteria=["Given X", "When Y"],
            complexity="M",
        )
    ]
    csv_str = stories_to_jira_csv_string(stories)
    assert "Add SSO" in csv_str
    assert "Summary" in csv_str
    assert "M" in csv_str
