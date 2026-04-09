"""Helpers for rough token estimation."""


def estimate_token_count(text: str) -> int:
    """Estimate token count using a simple word-based heuristic."""

    if not text.strip():
        return 0
    return max(1, len(text.split()))
