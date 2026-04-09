from app.models.schemas import PersonaDossier, ResponsePlan, SessionMemory
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoader
from app.services.question_classifier import QuestionClassifier
from app.services.response_planner import ResponsePlanner
from app.services.simple_verifier import SimpleVerifier


class FakeResponseGenerator:
    def generate(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        response_plan: ResponsePlan,
    ) -> str:
        del user_question
        del dossier
        del memory
        del response_plan
        return (
            "Curiosity matters more than certainty, because questioning is the beginning of understanding."
        )


class BadResponseGenerator:
    def generate(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        response_plan: ResponsePlan,
    ) -> str:
        del user_question
        del dossier
        del memory
        del response_plan
        return "I have seen how AI transformed society, and I support it."


def test_chat_service_returns_pipeline_result() -> None:
    persona_loader = PersonaLoader("app/personas")
    memory_service = MemoryService()
    question_classifier = QuestionClassifier()
    response_planner = ResponsePlanner()
    response_generator = FakeResponseGenerator()

    chat_service = ChatService(
        persona_loader=persona_loader,
        memory_service=memory_service,
        question_classifier=question_classifier,
        response_planner=response_planner,
        response_generator=response_generator,
        response_verifier=None,
    )

    result = chat_service.chat(
        session_id="session1",
        figure_id="einstein",
        user_question="What matters most in discovery?",
    )

    assert "Curiosity matters more than certainty" in result.final_answer
    assert result.classification.question_type == "philosophical"


def test_chat_service_uses_failsafe_when_verifier_fails() -> None:
    persona_loader = PersonaLoader("app/personas")
    memory_service = MemoryService()
    question_classifier = QuestionClassifier()
    response_planner = ResponsePlanner()
    response_generator = BadResponseGenerator()
    response_verifier = SimpleVerifier()

    chat_service = ChatService(
        persona_loader=persona_loader,
        memory_service=memory_service,
        question_classifier=question_classifier,
        response_planner=response_planner,
        response_generator=response_generator,
        response_verifier=response_verifier,
    )

    result = chat_service.chat(
        session_id="session2",
        figure_id="einstein",
        user_question="What do you think about AI today?",
    )

    assert "I would rather answer cautiously than pretend certainty." in result.final_answer
    assert result.verifier_result is not None
    assert result.verifier_result.status == "fail_safe"
