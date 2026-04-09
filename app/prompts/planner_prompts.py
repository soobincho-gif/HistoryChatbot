"""Planner prompt templates."""

PLANNER_PROMPT_TEMPLATE = """
Analyze the user's question and return a structured plan.

Decide:
- question type,
- temporal context,
- whether the answer is within the figure's knowledge boundary,
- what stance to take,
- whether uncertainty or evidence should be emphasized.
""".strip()
