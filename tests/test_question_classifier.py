from app.services.persona_loader import PersonaLoader
from app.services.question_classifier import QuestionClassifier


def test_classifier_detects_posthumous_question() -> None:
    loader = PersonaLoader("app/personas")
    dossier = loader.load("einstein")

    classifier = QuestionClassifier()
    result = classifier.classify("What do you think about AI today?", dossier)

    assert result.question_type == "posthumous_current_events"
    assert result.is_posthumous is True
    assert result.requires_caution is True


def test_classifier_detects_philosophical_question() -> None:
    loader = PersonaLoader("app/personas")
    dossier = loader.load("gandhi")

    classifier = QuestionClassifier()
    result = classifier.classify("What do you think matters most in freedom?", dossier)

    assert result.question_type == "philosophical"
    assert result.answer_mode == "reflective_opinion"
