"""Helpers for small text normalization tasks."""


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces."""

    return " ".join(text.split())


def truncate_text(text: str, max_length: int) -> str:
    """Return text truncated to the requested length."""

    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return text[:max_length]
    return f"{text[: max_length - 3]}..."
