from __future__ import annotations

import re

from app.models.schemas import PersonaDossier, QuestionClassification


class QuestionClassifier:
    """
    Rule-based MVP classifier.

    Later, this can be replaced or augmented with an LLM-based classifier.
    For now, the goal is to reliably catch:
    - posthumous/current-event questions
    - philosophical/opinion questions
    - personal-life questions
    - counterfactual questions
    - straightforward factual questions
    """

    MODERN_KEYWORDS = {
        "ai",
        "artificial intelligence",
        "internet",
        "smartphone",
        "social media",
        "climate change",
        "democracy",
        "capitalism",
        "cryptocurrency",
        "bitcoin",
        "chatgpt",
        "robot",
        "machine learning",
        "deep learning",
        "modern",
        "today",
        "now",
        "current",
    }

    PHILOSOPHICAL_CUES = {
        "what do you think",
        "do you believe",
        "what is",
        "what matters",
        "should",
        "is it right",
        "is it moral",
        "what would you say",
        "how should",
    }

    PERSONAL_CUES = {
        "were you",
        "did you feel",
        "were you lonely",
        "were you afraid",
        "what kind of person",
        "what were you like",
        "did power change you",
        "how did you feel",
    }

    COUNTERFACTUAL_CUES = {
        "what if",
        "if you had",
        "if you were alive today",
        "if you lived today",
        "suppose",
        "imagine if",
    }

    FACTUAL_CUES = {
        "when did",
        "where did",
        "who was",
        "who were",
        "why did",
        "how did",
        "what happened",
        "what was your role",
    }

    def classify(self, user_question: str, dossier: PersonaDossier) -> QuestionClassification:
        normalized = self._normalize(user_question)

        is_posthumous = self._detect_posthumous(normalized, dossier)
        is_counterfactual = self._contains_any(normalized, self.COUNTERFACTUAL_CUES)
        is_personal = self._contains_any(normalized, self.PERSONAL_CUES)
        is_philosophical = self._contains_any(normalized, self.PHILOSOPHICAL_CUES)
        is_factual = self._contains_any(normalized, self.FACTUAL_CUES)

        if self._needs_clarification(normalized):
            return QuestionClassification(
                question_type="ambiguous",
                requires_caution=False,
                is_posthumous=False,
                should_refuse_direct_claim=False,
                answer_mode="clarifying_question",
                needs_clarification=True,
                reasoning_note="The question is too short or vague to answer clearly.",
            )

        if is_counterfactual and is_posthumous:
            return QuestionClassification(
                question_type="counterfactual",
                requires_caution=True,
                is_posthumous=True,
                should_refuse_direct_claim=True,
                answer_mode="cautious_historical_projection",
                needs_clarification=False,
                reasoning_note="The question asks for a hypothetical response in a modern or posthumous context.",
            )

        if is_posthumous:
            return QuestionClassification(
                question_type="posthumous_current_events",
                requires_caution=True,
                is_posthumous=True,
                should_refuse_direct_claim=True,
                answer_mode="cautious_historical_projection",
                needs_clarification=False,
                reasoning_note="The question references modern topics or events beyond the figure's lifetime.",
            )

        if is_counterfactual:
            return QuestionClassification(
                question_type="counterfactual",
                requires_caution=True,
                is_posthumous=False,
                should_refuse_direct_claim=False,
                answer_mode="reflective_opinion",
                needs_clarification=False,
                reasoning_note="The question is hypothetical and should be answered cautiously in character.",
            )

        if is_personal:
            return QuestionClassification(
                question_type="personal_life",
                requires_caution=True,
                is_posthumous=False,
                should_refuse_direct_claim=False,
                answer_mode="direct_in_character",
                needs_clarification=False,
                reasoning_note="The question concerns the figure's inner life, temperament, or private experience.",
            )

        if is_philosophical:
            return QuestionClassification(
                question_type="philosophical",
                requires_caution=False,
                is_posthumous=False,
                should_refuse_direct_claim=False,
                answer_mode="reflective_opinion",
                needs_clarification=False,
                reasoning_note="The question asks for principles, interpretation, or reflective judgment.",
            )

        if is_factual:
            return QuestionClassification(
                question_type="factual",
                requires_caution=False,
                is_posthumous=False,
                should_refuse_direct_claim=False,
                answer_mode="direct_in_character",
                needs_clarification=False,
                reasoning_note="The question appears to request a direct historical or biographical answer.",
            )

        return QuestionClassification(
            question_type="philosophical",
            requires_caution=False,
            is_posthumous=False,
            should_refuse_direct_claim=False,
            answer_mode="reflective_opinion",
            needs_clarification=False,
            reasoning_note="Fallback classification: the question is open-ended and best treated as reflective.",
        )

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _contains_any(self, text: str, candidates: set[str]) -> bool:
        return any(candidate in text for candidate in candidates)

    def _detect_posthumous(self, text: str, dossier: PersonaDossier) -> bool:
        if self._contains_any(text, self.MODERN_KEYWORDS):
            return True

        years = re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", text)
        if years and dossier.death_year is not None:
            for year_text in years:
                if int(year_text) > dossier.death_year:
                    return True

        phrases = [
            "today",
            "in modern times",
            "in the modern world",
            "current society",
            "these days",
            "the world now",
        ]
        return any(phrase in text for phrase in phrases)

    def _needs_clarification(self, text: str) -> bool:
        if len(text) <= 2:
            return True

        vague_patterns = {
            "what about that",
            "and then",
            "so?",
            "thoughts?",
            "explain",
        }
        return text in vague_patterns
