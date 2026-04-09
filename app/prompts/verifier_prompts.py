"""Verifier prompt templates."""

VERIFIER_PROMPT_TEMPLATE = """
Review the draft answer for:
- persona consistency,
- directness in answering the user,
- anachronistic certainty,
- unsupported claims,
- mismatch with the response plan.

Return pass, warn, or fail with concise issue notes.
""".strip()
