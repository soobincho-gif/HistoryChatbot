from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoader
from app.services.question_classifier import QuestionClassifier
from app.services.response_planner import ResponsePlanner


def test_response_planner_sets_limits_for_posthumous_question() -> None:
    loader = PersonaLoader("app/personas")
    dossier = loader.load("einstein")

    memory_service = MemoryService()
    memory_service.create_session(session_id="s1", figure_id="einstein")
    memory = memory_service.get_session("s1")

    classifier = QuestionClassifier()
    classification = classifier.classify("What do you think of modern AI?", dossier)

    planner = ResponsePlanner()
    plan = planner.build_plan(
        user_question="What do you think of modern AI?",
        dossier=dossier,
        memory=memory,
        classification=classification,
    )

    assert plan.mention_limits is True
    assert "Do not claim direct lived experience of modern events." in plan.avoid_claims
