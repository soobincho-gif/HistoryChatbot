from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoader
from app.services.simple_verifier import SimpleVerifier


def test_verifier_flags_generic_ai_language() -> None:
    loader = PersonaLoader("app/personas")
    dossier = loader.load("einstein")

    memory_service = MemoryService()
    memory_service.create_session(session_id="s1", figure_id="einstein")
    memory = memory_service.get_session("s1")

    verifier = SimpleVerifier()
    result = verifier.verify(
        user_question="What do you think about time?",
        dossier=dossier,
        memory=memory,
        draft_answer="As an AI language model, I think time is relative.",
    )

    assert result.status in {"revise", "fail_safe"}
    assert any(issue.issue_type == "generic_tone" for issue in result.issues)


def test_verifier_flags_modern_direct_experience() -> None:
    loader = PersonaLoader("app/personas")
    dossier = loader.load("einstein")

    memory_service = MemoryService()
    memory_service.create_session(session_id="s2", figure_id="einstein")
    memory = memory_service.get_session("s2")

    verifier = SimpleVerifier()
    result = verifier.verify(
        user_question="What do you think about AI?",
        dossier=dossier,
        memory=memory,
        draft_answer="I have seen how AI transformed society, and I fully support it.",
    )

    assert result.status == "fail_safe"
    assert any(issue.issue_type in {"anachronism", "historical_overreach"} for issue in result.issues)
