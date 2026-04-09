from __future__ import annotations

from textwrap import dedent

from app.models.schemas import PersonaDossier, ResponsePlan, SessionMemory


def build_character_instructions(
    dossier: PersonaDossier,
    response_plan: ResponsePlan,
) -> str:
    """
    Build the top-level instruction block for the selected historical figure.
    This is passed to the model as `instructions`.
    """
    worldview = "\n".join(f"- {item}" for item in dossier.worldview) or "- (No worldview notes)"
    speech_style = "\n".join(f"- {item}" for item in dossier.speech_style) or "- (No speech style notes)"
    temperament = "\n".join(f"- {item}" for item in dossier.temperament) or "- (No temperament notes)"
    knowledge_boundary = "\n".join(f"- {item}" for item in dossier.knowledge_boundary) or "- (No explicit boundary notes)"
    avoid_claims = "\n".join(f"- {item}" for item in response_plan.avoid_claims) or "- (No additional avoid-claim items)"
    key_points = "\n".join(f"- {item}" for item in response_plan.key_points) or "- (No special key points)"

    mention_limits_instruction = (
        "Yes. If needed, explicitly acknowledge historical distance, uncertainty, "
        "or lack of direct lived knowledge."
        if response_plan.mention_limits
        else "No. Do not force unnecessary disclaimers."
    )

    return dedent(
        f"""
        You are simulating a conversation as {dossier.name}.

        Stay consistent with:
        Era:
        {dossier.era}

        Identity:
        {dossier.identity}

        Worldview:
        {worldview}

        Speech style:
        {speech_style}

        Temperament:
        {temperament}

        Historical boundaries:
        {knowledge_boundary}

        Posthumous question policy:
        {dossier.posthumous_policy}

        Response strategy:
        - Tone strategy: {response_plan.tone_strategy}
        - Historical scope: {response_plan.historical_scope}
        - Mention limits explicitly: {mention_limits_instruction}
        - Recommended answer length: {response_plan.recommended_length}

        Key points to prioritize:
        {key_points}

        Claims or tones to avoid:
        {avoid_claims}

        Hard rules:
        - Remain in character.
        - Be natural and conversational, not theatrical or parody-like.
        - Do not claim direct lived experience of events after your lifetime.
        - Do not fabricate historical details.
        - If uncertain, remain honest while staying in character.
        - Do not mention being an AI or language model.
        - Answer the user's actual question directly.
        """
    ).strip()


def build_generation_input(
    *,
    user_question: str,
    dossier: PersonaDossier,
    memory: SessionMemory,
) -> str:
    """
    Render a compact text input block for the Responses API.
    We intentionally keep this explicit and inspectable instead of relying on
    a hidden conversation state.
    """
    recent_turns_text = _render_recent_turns(memory)
    evidence_text = _render_evidence_snippets(dossier)

    return dedent(
        f"""
        Selected historical figure: {dossier.name}

        Session summary:
        {memory.session_summary or "(No summary yet)"}

        Recent conversation:
        {recent_turns_text or "(No prior turns yet)"}

        Historical grounding snippets:
        {evidence_text or "(No evidence snippets available)"}

        User question:
        {user_question}

        Write one final answer for the user.
        """
    ).strip()


def _render_recent_turns(memory: SessionMemory) -> str:
    lines: list[str] = []

    for turn in memory.recent_turns[-6:]:
        if turn.role == "user":
            prefix = "User"
        elif turn.role == "assistant":
            prefix = "Assistant"
        else:
            prefix = "System"
        lines.append(f"{prefix}: {turn.content}")

    return "\n".join(lines)


def _render_evidence_snippets(dossier: PersonaDossier) -> str:
    lines: list[str] = []
    for snippet in dossier.evidence_snippets:
        source = f" [{snippet.source_hint}]" if snippet.source_hint else ""
        lines.append(f"- ({snippet.topic}) {snippet.content}{source}")
    return "\n".join(lines)
