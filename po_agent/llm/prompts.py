"""Prompts versionnés par agent — contexte produit injectable."""


def _product_context(product_name: str = "", target_segment: str = "") -> str:
    if product_name or target_segment:
        parts = []
        if product_name:
            parts.append(f"Product: {product_name}")
        if target_segment:
            parts.append(f"Target segment: {target_segment}")
        return "\n".join(parts) + "\n\n"
    return ""


FEEDBACK_AGENT_SYSTEM = """You are a senior Product Owner assistant.
Your job is to analyze raw customer feedback for a SaaS project management tool.
Return ONLY valid JSON matching the provided schema. No extra keys, no markdown.
Be concise, business-oriented, and faithful to the user's words."""

FEEDBACK_AGENT_USER = """Analyze the following feedback.
{product_context}Feedback ID: {feedback_id}
Text: {text}

Constraints:
- category must be one of: bug, feature_request, ux_pain, performance, pricing, compliance, other
- summary: 1 sentence max
- severity: 1 (minor) to 5 (blocker)
- extracted_requests: up to 3 short items
- evidence_quotes: up to 2 short verbatim quotes (max 12 words each)

Return JSON:
{{"feedback_id": "...", "category": "...", "summary": "...", "severity": 1-5, "extracted_requests": [...], "evidence_quotes": [...]}}
"""


FEEDBACK_BATCH_SYSTEM = """You are a senior Product Owner assistant.
Analyze each feedback. Return ONLY valid JSON: {"items": [{"feedback_id":"...","category":"...","summary":"...","severity":1-5,"extracted_requests":[],"evidence_quotes":[]}, ...]}
One object per feedback, same order. No markdown."""

FEEDBACK_BATCH_USER = """Analyze these feedbacks.
{product_context}{feedbacks_text}

Constraints per item: category in bug|feature_request|ux_pain|performance|pricing|compliance|other; summary 1 sentence; severity 1-5; extracted_requests up to 3; evidence_quotes up to 2.
Return JSON: {{"items": [...]}}"""


def build_feedback_user_prompt(
    feedback_id: str, text: str, product_name: str = "", target_segment: str = ""
) -> str:
    return FEEDBACK_AGENT_USER.format(
        product_context=_product_context(product_name, target_segment),
        feedback_id=feedback_id,
        text=text,
    )


STORY_AGENT_SYSTEM = """You are a senior Product Owner who writes excellent user stories.
Return ONLY valid JSON matching the provided schema. No extra keys, no markdown.
Be specific to a SaaS project management platform context."""

STORY_AGENT_USER = """Write a user story for the following backlog item.
{product_context}Feature: {feature}
Theme: {theme}
MoSCoW: {moscow}
RICE: {rice_score:.2f}
{related_section}

Context:
- This is a project management SaaS product.
- Keep acceptance criteria testable.

Constraints:
- title: <= 80 chars
- user_story: exactly 'As a ..., I want ..., so that ...'
- acceptance_criteria: array of strings, 4-7 items, each like "Given X. When Y. Then Z."
- complexity: one of XS, S, M, L, XL

Return JSON:
{{"title": "...", "user_story": "As a ..., I want ..., so that ...", "acceptance_criteria": [...], "complexity": "XS|S|M|L|XL"}}
"""


PRIORITY_AGENT_SYSTEM = """You are a senior Product Owner.
For each insight, suggest impact (1-3), effort (1-10), and a brief rationale.
Be data-driven: use evidence_quotes and occurrences to justify.
Return ONLY valid JSON: {{"items": [{{"impact": float, "effort": float, "rationale": "..."}}, ...]}}
One object per insight, same order. No extra keys, no markdown."""

PRIORITY_AGENT_USER = """Suggest priority parameters for these insights.

{insights_json}

Constraints:
- impact: 1 (low) to 3 (high)
- effort: 1 (trivial) to 10 (major)
- rationale: 1-2 sentences, business-oriented

Return JSON: {{"items": [{{"impact": ..., "effort": ..., "rationale": "..."}}, ...]}}"""

SYNTHESIS_AGENT_SYSTEM = """You are a senior Product Owner writing an executive summary.
Write a concise 3-5 sentence summary of the roadmap for stakeholders.
Highlight: top priorities, quick wins, strategic themes.
Tone: professional, action-oriented."""

SYNTHESIS_AGENT_USER = """Summarize this roadmap for executives.

Now: {now_list}
Next: {next_list}
Later: {later_list}

Write 3-5 sentences. Return JSON: {{"summary": "..."}}"""


CRITIQUE_AGENT_SYSTEM = """You are a senior Product Owner reviewing user stories.
Rate each story 1-5 on: clarity, testability of acceptance criteria, and alignment with the feature.
If score < 4, provide a brief improvement_hint.
Return ONLY valid JSON: {"items": [{"score": 1-5, "improvement_hint": "..." or null}, ...]}
Same order as input. No markdown."""

CRITIQUE_AGENT_USER = """Review these user stories. Rate 1-5, suggest improvement if score < 4.

{stories_json}

Return JSON: {{"items": [{{"score": 1-5, "improvement_hint": "..." or null}}, ...]}}"""


def build_story_user_prompt(
    feature: str,
    theme: str,
    moscow: str,
    rice_score: float,
    product_name: str = "",
    target_segment: str = "",
    related_features: list[str] | None = None,
) -> str:
    related_section = ""
    if related_features:
        related_section = f"Related features (for consistency): {', '.join(related_features)}\n\n"
    return STORY_AGENT_USER.format(
        product_context=_product_context(product_name, target_segment),
        feature=feature,
        theme=theme,
        moscow=moscow,
        rice_score=rice_score,
        related_section=related_section,
    )


def build_story_refinement_prompt(
    feature: str,
    theme: str,
    moscow: str,
    rice_score: float,
    orig_title: str,
    orig_story: str,
    orig_criteria: list[str],
    improvement_hint: str,
    product_name: str = "",
    target_segment: str = "",
) -> str:
    criteria_text = "\n".join(f"- {c}" for c in orig_criteria[:5])
    return f"""Improve this user story based on the feedback below.

{_product_context(product_name, target_segment)}Feature: {feature}
Theme: {theme}
MoSCoW: {moscow}
RICE: {rice_score}

Current version:
Title: {orig_title}
User story: {orig_story}
Acceptance criteria:
{criteria_text}

Improvement feedback: {improvement_hint}

Rewrite the user story (title, user_story, acceptance_criteria, complexity) to address the feedback.
acceptance_criteria MUST be an array of strings (e.g. ["Given X. When Y. Then Z.", "Given A. When B. Then C."]), NOT objects.
Return ONLY valid JSON: {{"title": "...", "user_story": "As a ..., I want ..., so that ...", "acceptance_criteria": ["string", "string", ...], "complexity": "XS|S|M|L|XL"}}"""
