from app.models import ChatTurn, PersonaDossier, ResponsePlan, SessionMemory
from app.prompts.system_prompts import (
    build_character_instructions,
    build_generation_input,
)
from app.services.persona_loader import PersonaLoader


def test_build_character_instructions_includes_plan_and_boundaries() -> None:
    dossier = PersonaLoader("app/personas").load("einstein")
    plan = ResponsePlan(
        tone_strategy="Thoughtful and clear.",
        historical_scope="Stay within Einstein's perspective.",
        mention_limits=True,
        key_points=["Answer directly first."],
        avoid_claims=["Do not claim direct lived experience of modern events."],
        recommended_length="medium",
    )

    instructions = build_character_instructions(dossier=dossier, response_plan=plan)

    assert "You are simulating a conversation as Albert Einstein." in instructions
    assert "Do not claim direct lived experience of modern events." in instructions
    assert "Recommended answer length: medium" in instructions


def test_build_generation_input_renders_memory_and_evidence() -> None:
    dossier = PersonaLoader("app/personas").load("gandhi")
    memory = SessionMemory(
        session_id="s1",
        figure_id="gandhi",
        recent_turns=[
            ChatTurn(role="user", content="What is truth?"),
            ChatTurn(role="assistant", content="Truth demands discipline."),
        ],
        session_summary="The discussion centered on truth and moral discipline.",
    )

    rendered = build_generation_input(
        user_question="How should truth shape politics?",
        dossier=dossier,
        memory=memory,
    )

    assert "Session summary:" in rendered
    assert "User: What is truth?" in rendered
    assert "Assistant: Truth demands discipline." in rendered
    assert "Historical grounding snippets:" in rendered
    assert "How should truth shape politics?" in rendered
