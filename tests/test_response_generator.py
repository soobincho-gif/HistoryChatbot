from app.config import AppConfig
from app.models import ResponsePlan, SessionMemory
from app.services.persona_loader import PersonaLoader
from app.services.response_generator import OpenAIResponseGenerator


class DummyResponse:
    def __init__(self, output_text=None, output=None) -> None:
        self.output_text = output_text
        self.output = output


class DummyResponsesAPI:
    def __init__(self, response: DummyResponse) -> None:
        self._response = response

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return self._response


class DummyClient:
    def __init__(self, response: DummyResponse) -> None:
        self.responses = DummyResponsesAPI(response)


def test_response_generator_prefers_output_text() -> None:
    dossier = PersonaLoader("app/personas").load("einstein")
    memory = SessionMemory(session_id="s1", figure_id="einstein")
    plan = ResponsePlan(
        tone_strategy="Thoughtful and reflective.",
        historical_scope="Stay within Einstein's perspective.",
        mention_limits=False,
        key_points=["Answer the question directly."],
        avoid_claims=[],
        recommended_length="medium",
    )
    generator = OpenAIResponseGenerator(AppConfig(openai_api_key="test-key"))
    generator.client = DummyClient(DummyResponse(output_text="Curiosity matters most."))

    result = generator.generate(
        user_question="What matters in discovery?",
        dossier=dossier,
        memory=memory,
        response_plan=plan,
    )

    assert result == "Curiosity matters most."


def test_response_generator_uses_fallback_parser_when_output_text_is_empty() -> None:
    dossier = PersonaLoader("app/personas").load("cleopatra")
    memory = SessionMemory(session_id="s2", figure_id="cleopatra")
    plan = ResponsePlan(
        tone_strategy="Elegant and controlled.",
        historical_scope="Stay within Cleopatra's perspective.",
        mention_limits=True,
        key_points=["Answer cautiously."],
        avoid_claims=[],
        recommended_length="short",
    )
    output = [
        {
            "content": [
                {"text": "Power belongs to those"},
                {"text": " who read the room well."},
            ]
        }
    ]
    generator = OpenAIResponseGenerator(AppConfig(openai_api_key="test-key"))
    generator.client = DummyClient(DummyResponse(output_text="", output=output))

    result = generator.generate(
        user_question="What is leadership?",
        dossier=dossier,
        memory=memory,
        response_plan=plan,
    )

    assert result == "Power belongs to those\nwho read the room well."
