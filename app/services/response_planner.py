from __future__ import annotations

from app.models.schemas import (
    PersonaDossier,
    QuestionClassification,
    ResponsePlan,
    SessionMemory,
)


class ResponsePlanner:
    """Convert a question analysis into generation instructions."""

    def build_plan(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        classification: QuestionClassification,
    ) -> ResponsePlan:
        """
        Converts question classification + persona + memory into a structured response plan.

        This does not generate final prose.
        It only decides how the answer should be framed.
        """
        tone_strategy = self._build_tone_strategy(dossier, classification, memory)
        historical_scope = self._build_historical_scope(dossier, classification)
        mention_limits = classification.requires_caution or classification.is_posthumous

        key_points = self._build_key_points(
            user_question=user_question,
            dossier=dossier,
            memory=memory,
            classification=classification,
        )
        avoid_claims = self._build_avoid_claims(dossier, classification)

        return ResponsePlan(
            tone_strategy=tone_strategy,
            historical_scope=historical_scope,
            mention_limits=mention_limits,
            key_points=key_points,
            avoid_claims=avoid_claims,
            recommended_length=memory.user_preferences.preferred_answer_length,
        )

    def _build_tone_strategy(
        self,
        dossier: PersonaDossier,
        classification: QuestionClassification,
        memory: SessionMemory,
    ) -> str:
        del memory
        base_style = (
            ", ".join(dossier.speech_style[:3]) if dossier.speech_style else "clear and in character"
        )

        if classification.question_type == "factual":
            return f"Answer clearly and naturally in character, using a {base_style} style."

        if classification.question_type == "philosophical":
            return (
                f"Answer reflectively in character, emphasizing worldview and principles "
                f"with a {base_style} style."
            )

        if classification.question_type == "personal_life":
            return (
                f"Answer with emotional restraint and plausibility in character, "
                f"using a {base_style} style."
            )

        if classification.question_type == "posthumous_current_events":
            return (
                f"Answer cautiously in character, applying the figure's principles to a modern issue "
                f"without pretending direct experience, using a {base_style} style."
            )

        if classification.question_type == "counterfactual":
            return (
                f"Answer carefully in character, treating the question as hypothetical while staying grounded "
                f"in the figure's worldview and temperament, using a {base_style} style."
            )

        return f"Ask a brief clarifying question in character, using a {base_style} style."

    def _build_historical_scope(
        self,
        dossier: PersonaDossier,
        classification: QuestionClassification,
    ) -> str:
        if classification.is_posthumous:
            return (
                f"Stay within {dossier.name}'s historical perspective and principles. "
                f"Do not claim direct knowledge of events after {dossier.death_year}."
            )

        if classification.question_type == "personal_life":
            return (
                "Stay close to broadly plausible biography and temperament. "
                "Avoid intimate or highly specific invented details."
            )

        if classification.question_type == "factual":
            return (
                "Stay close to well-known biographical and historical facts. "
                "Do not invent precise details unless strongly grounded."
            )

        return (
            "Stay within the figure's era, worldview, and known intellectual style. "
            "Use inference carefully where direct certainty is not possible."
        )

    def _build_key_points(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        classification: QuestionClassification,
    ) -> list[str]:
        del user_question
        del dossier
        key_points: list[str] = []

        if classification.question_type == "factual":
            key_points.extend(
                [
                    "Answer the question directly first.",
                    "Keep the answer concrete and readable.",
                    "Use the figure's voice without becoming theatrical.",
                ]
            )

        elif classification.question_type == "philosophical":
            key_points.extend(
                [
                    "Lead with the figure's guiding principle.",
                    "Connect the answer to worldview or moral/intellectual beliefs.",
                    "Keep the answer natural rather than lecture-like.",
                ]
            )

        elif classification.question_type == "personal_life":
            key_points.extend(
                [
                    "Respond with plausible introspection, not invented diary-level detail.",
                    "Keep emotional tone controlled and believable.",
                    "Reflect temperament and worldview.",
                ]
            )

        elif classification.question_type == "posthumous_current_events":
            key_points.extend(
                [
                    "Acknowledge historical distance if needed.",
                    "Answer through analogy, principle, or inferred judgment.",
                    "Do not claim firsthand knowledge of the modern topic.",
                ]
            )

        elif classification.question_type == "counterfactual":
            key_points.extend(
                [
                    "Treat the question as hypothetical.",
                    "Anchor the answer in known values and tendencies.",
                    "Avoid overconfident certainty.",
                ]
            )

        else:
            key_points.extend(
                [
                    "Ask a short clarifying question.",
                    "Stay in character.",
                ]
            )

        if memory.session_summary:
            key_points.append("Use the current session context when relevant.")

        if memory.user_preferences.wants_simple_explanations:
            key_points.append("Prefer simple, clear explanation over dense abstraction.")

        if memory.user_preferences.prefers_more_historical_detail:
            key_points.append("Include a bit more historical context than usual.")

        return key_points

    def _build_avoid_claims(
        self,
        dossier: PersonaDossier,
        classification: QuestionClassification,
    ) -> list[str]:
        avoid_claims = list(dossier.taboo_or_uncertain_topics)

        if classification.is_posthumous:
            avoid_claims.extend(
                [
                    "Do not claim direct lived experience of modern events.",
                    "Do not speak as though the figure has studied contemporary institutions firsthand.",
                ]
            )

        if classification.question_type == "personal_life":
            avoid_claims.extend(
                [
                    "Do not invent precise private emotions as if quoting a diary.",
                    "Do not make melodramatic self-descriptions unsupported by biography.",
                ]
            )

        if classification.question_type == "factual":
            avoid_claims.extend(
                [
                    "Do not fabricate dates, names, or detailed events.",
                ]
            )

        return avoid_claims
