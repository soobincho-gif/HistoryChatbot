from __future__ import annotations

from app.models.schemas import (
    PersonaDossier,
    SessionMemory,
    VerifierIssue,
    VerifierResult,
)
from app.services.verifier import ResponseVerifier


class SimpleVerifier(ResponseVerifier):
    """
    Rule-based `ResponseVerifier` implementation for the MVP.

    Goals:
    - catch obvious persona drift
    - catch direct modern-experience claims
    - catch generic assistant phrasing
    - catch likely non-answers
    """

    GENERIC_AI_PATTERNS = [
        "as an ai",
        "as a language model",
        "i am an ai",
        "i cannot browse",
        "i do not have personal opinions",
    ]

    MODERN_EXPERIENCE_PATTERNS = [
        "i have seen the internet",
        "i use smartphones",
        "i have studied modern ai",
        "i watched social media",
        "i have experienced today's world",
        "i have seen how ai transformed society",
    ]

    NON_ANSWER_PATTERNS = [
        "that is difficult to say",
        "it depends",
        "there are many perspectives",
    ]

    def verify(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        draft_answer: str,
    ) -> VerifierResult:
        issues: list[VerifierIssue] = []

        del memory
        normalized = draft_answer.lower().strip()

        issues.extend(self._check_generic_ai_language(normalized))
        issues.extend(self._check_modern_experience_claims(normalized, dossier))
        issues.extend(self._check_non_answer(user_question, normalized))
        issues.extend(self._check_basic_persona_style(dossier, normalized))

        if not issues:
            return VerifierResult(
                status="pass",
                issues=[],
                suggested_fix=None,
            )

        severe_issue_types = {
            "historical_overreach",
            "anachronism",
        }
        if any(issue.issue_type in severe_issue_types for issue in issues):
            return VerifierResult(
                status="fail_safe",
                issues=issues,
                suggested_fix=(
                    "Regenerate with stronger historical-boundary constraints and explicit "
                    "posthumous caution."
                ),
            )

        return VerifierResult(
            status="revise",
            issues=issues,
            suggested_fix=(
                "Regenerate with stronger persona anchoring and more direct question answering."
            ),
        )

    def _check_generic_ai_language(self, text: str) -> list[VerifierIssue]:
        issues: list[VerifierIssue] = []

        for pattern in self.GENERIC_AI_PATTERNS:
            if pattern in text:
                issues.append(
                    VerifierIssue(
                        issue_type="generic_tone",
                        description=(
                            f"Response contains generic assistant phrasing: '{pattern}'."
                        ),
                    )
                )

        return issues

    def _check_modern_experience_claims(
        self,
        text: str,
        dossier: PersonaDossier,
    ) -> list[VerifierIssue]:
        issues: list[VerifierIssue] = []

        for pattern in self.MODERN_EXPERIENCE_PATTERNS:
            if pattern in text:
                issues.append(
                    VerifierIssue(
                        issue_type="anachronism",
                        description=(
                            f"Response implies direct experience of a modern phenomenon: '{pattern}'."
                        ),
                    )
                )

        if dossier.death_year is not None:
            impossible_direct_claim_markers = [
                "in today's world i have seen",
                "when i looked at modern society",
                "i know from direct experience that modern",
            ]
            for pattern in impossible_direct_claim_markers:
                if pattern in text:
                    issues.append(
                        VerifierIssue(
                            issue_type="historical_overreach",
                            description=(
                                "Response appears to claim direct knowledge beyond the figure's lifetime."
                            ),
                        )
                    )

        return issues

    def _check_non_answer(
        self,
        user_question: str,
        text: str,
    ) -> list[VerifierIssue]:
        issues: list[VerifierIssue] = []

        short_question = len(user_question.split()) >= 4
        very_short_answer = len(text.split()) < 6

        if short_question and very_short_answer:
            issues.append(
                VerifierIssue(
                    issue_type="non_answer",
                    description="Response is too short to plausibly answer the user's question.",
                )
            )
            return issues

        if all(pattern in text for pattern in ["it depends", "many perspectives"]):
            issues.append(
                VerifierIssue(
                    issue_type="non_answer",
                    description="Response is vague and evasive.",
                )
            )
            return issues

        if any(pattern == text for pattern in self.NON_ANSWER_PATTERNS):
            issues.append(
                VerifierIssue(
                    issue_type="non_answer",
                    description="Response is generic and does not answer the question directly.",
                )
            )

        return issues

    def _check_basic_persona_style(
        self,
        dossier: PersonaDossier,
        text: str,
    ) -> list[VerifierIssue]:
        """
        Very lightweight heuristic.
        We do NOT want parody enforcement.
        We only want to catch obviously flat/generic phrasing.
        """
        issues: list[VerifierIssue] = []

        style_hint_words = []
        for item in dossier.speech_style:
            style_hint_words.extend(item.lower().split())

        worldview_hint_words = []
        for item in dossier.worldview:
            worldview_hint_words.extend(item.lower().split())

        overlap_candidates = set(style_hint_words + worldview_hint_words)
        overlap_candidates = {
            token.strip(".,!?;:()[]{}\"'")
            for token in overlap_candidates
            if len(token) >= 6
        }

        overlap_count = sum(1 for token in overlap_candidates if token in text)

        if len(text.split()) >= 20 and overlap_count == 0:
            issues.append(
                VerifierIssue(
                    issue_type="persona_drift",
                    description=(
                        "Longer response shows weak overlap with persona style/worldview cues."
                    ),
                )
            )

        return issues
