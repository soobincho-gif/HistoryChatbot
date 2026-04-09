import json

from app.models.schemas import PersonaDossier, ResponsePlan, SessionMemory
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService
from app.services.persona_registry import PersonaRegistry
from app.services.question_classifier import QuestionClassifier
from app.services.response_planner import ResponsePlanner
from app.services.simple_verifier import SimpleVerifier


class CustomFlowResponseGenerator:
    def generate(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        response_plan: ResponsePlan,
    ) -> str:
        del user_question
        del response_plan

        assert memory.figure_id == dossier.figure_id
        assert memory.recent_turns[-1].role == "user"

        return (
            f"{dossier.name}, speaking from disciplined imagination and analytical precision, "
            "would say that machines become meaningful when they expand human inquiry without "
            "pretending to replace judgment."
        )


def test_custom_persona_flow_smoke(tmp_path) -> None:
    preset_dir = tmp_path / "presets"
    custom_dir = tmp_path / "customs"
    preset_dir.mkdir()
    custom_dir.mkdir()

    preset_dossier = {
        "figure_id": "ada_lovelace",
        "name": "Preset Ada",
        "era": "Victorian Britain",
        "identity": "A preset dossier used to force a collision during custom save.",
        "worldview": [],
        "speech_style": [],
        "temperament": [],
        "core_topics": [],
        "knowledge_boundary": [],
        "posthumous_policy": "N/A",
        "taboo_or_uncertain_topics": [],
        "example_phrases": [],
        "evidence_snippets": [],
        "starter_prompts": [],
    }
    with (preset_dir / "ada_lovelace.json").open("w", encoding="utf-8") as file:
        json.dump(preset_dossier, file)

    registry = PersonaRegistry(preset_dir, custom_dir)

    draft_dossier = PersonaDossier(
        figure_id="Ada Lovelace",
        name="Ada Lovelace",
        era="Victorian Britain",
        birth_year=1815,
        death_year=1852,
        identity="Mathematician and writer who imagined new uses for computational engines.",
        worldview=["Disciplined imagination", "Analytical precision", "Poetic science"],
        speech_style=["Reflective precision", "Layered and mathematical"],
        temperament=["Curious", "Exacting"],
        core_topics=["Analytical Engine", "Mathematics", "Imagination"],
        knowledge_boundary=["No firsthand knowledge beyond the nineteenth century"],
        posthumous_policy="Speak as a nineteenth-century thinker projecting cautiously forward.",
        taboo_or_uncertain_topics=["Modern implementation details I could not have witnessed"],
        example_phrases=["The analytical engine weaves algebraic patterns."],
        evidence_snippets=[],
        starter_prompts=[
            "What did you think machines might become?",
            "Why does imagination matter in mathematics?",
            "What kind of future did you foresee for analytical engines?",
        ],
    )

    # Draft created and previewed before approval.
    assert draft_dossier.name == "Ada Lovelace"
    assert "computational engines" in draft_dossier.identity

    approved_id = registry.reserve_custom_figure_id(draft_dossier.figure_id)
    saved_dossier = registry.save_custom_persona(
        draft_dossier.model_copy(update={"figure_id": approved_id}),
    )

    assert saved_dossier.figure_id == "ada_lovelace_custom"
    assert registry.is_custom(saved_dossier.figure_id) is True
    assert registry.load(saved_dossier.figure_id).starter_prompts == draft_dossier.starter_prompts

    chat_service = ChatService(
        persona_loader=registry,
        memory_service=MemoryService(),
        question_classifier=QuestionClassifier(),
        response_planner=ResponsePlanner(),
        response_generator=CustomFlowResponseGenerator(),
        response_verifier=SimpleVerifier(),
    )

    session_id = "custom-smoke-session"
    chat_service.start_session(
        session_id=session_id,
        figure_id=saved_dossier.figure_id,
    )

    result = chat_service.chat(
        session_id=session_id,
        figure_id=saved_dossier.figure_id,
        user_question="What responsibility should inventors carry when they imagine new machines?",
    )

    memory = chat_service.memory_service.get_session(session_id)

    assert "disciplined imagination and analytical precision" in result.final_answer
    assert result.verifier_result is not None
    assert result.verifier_result.status == "pass"
    assert memory.figure_id == saved_dossier.figure_id
    assert [turn.role for turn in memory.recent_turns] == ["user", "assistant"]
    assert memory.recent_turns[0].content.startswith("What responsibility should inventors")
