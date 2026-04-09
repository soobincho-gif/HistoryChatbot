from app.models.schemas import PersonaDossier, SessionMemory
from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoader
from app.services.simple_verifier import SimpleVerifier
from app.services.verifier import NoOpVerifier, ResponseVerifier


def _load_verifier_context(session_id: str) -> tuple[PersonaDossier, SessionMemory]:
    loader = PersonaLoader("app/personas")
    dossier = loader.load("einstein")

    memory_service = MemoryService()
    memory_service.create_session(session_id=session_id, figure_id="einstein")
    memory = memory_service.get_session(session_id)

    return dossier, memory


def test_no_op_verifier_returns_pass_result() -> None:
    dossier, memory = _load_verifier_context("no-op")
    verifier = NoOpVerifier()

    result = verifier.verify(
        user_question="What matters most in discovery?",
        dossier=dossier,
        memory=memory,
        draft_answer="Curiosity matters more than certainty.",
    )

    assert result.status == "pass"
    assert result.issues == []
    assert result.suggested_fix is None


def test_simple_verifier_conforms_to_shared_contract() -> None:
    verifier: ResponseVerifier = SimpleVerifier()

    assert isinstance(verifier, ResponseVerifier)
