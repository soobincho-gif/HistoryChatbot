"""Shared verifier contract layer for post-generation quality checks."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models.schemas import PersonaDossier, SessionMemory, VerifierResult


@runtime_checkable
class ResponseVerifier(Protocol):
    """Contract for any component that validates a drafted answer."""

    def verify(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        draft_answer: str,
    ) -> VerifierResult:
        """Return a structured verification decision."""


class NoOpVerifier(ResponseVerifier):
    """Pass-through verifier used when quality gating is intentionally disabled."""

    def verify(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        draft_answer: str,
    ) -> VerifierResult:
        del user_question
        del dossier
        del memory
        del draft_answer
        return VerifierResult(status="pass", issues=[], suggested_fix=None)


__all__ = ["NoOpVerifier", "ResponseVerifier"]
