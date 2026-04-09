from unittest.mock import MagicMock, patch
import pytest

from app.config import AppConfig
from app.services.persona_builder import PersonaBuilderService, PersonaGenerationError
from app.services.starter_prompt_service import StarterPromptService, StarterPromptGenerationError
from app.models.schemas import PersonaDossier

@pytest.fixture
def dummy_config():
    return AppConfig(openai_api_key="test_key", openai_model="test_model", personas_dir="dummy", custom_personas_dir="dummy")

@patch("app.services.persona_builder.OpenAI")
def test_persona_builder_success(mock_openai_class, dummy_config):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '''
    {
      "figure_id": "test_fig",
      "name": "Test Figure",
      "era": "Test Era",
      "identity": "Test Identity",
      "worldview": ["Test"],
      "speech_style": ["Test"],
      "temperament": ["Test"],
      "core_topics": ["Test"],
      "knowledge_boundary": ["Test"],
      "posthumous_policy": "Test",
      "taboo_or_uncertain_topics": ["Test"],
      "example_phrases": ["Test"],
      "evidence_snippets": [{"topic": "T", "content": "C", "source_hint": "H"}],
      "starter_prompts": ["Q1?"]
    }
    '''
    mock_client.chat.completions.create.return_value = mock_response
    
    builder = PersonaBuilderService(dummy_config)
    dossier = builder.build_persona("Test Figure")
    
    assert dossier.name == "Test Figure"
    assert dossier.figure_id == "test_fig"
    assert "Q1?" in dossier.starter_prompts

@patch("app.services.starter_prompt_service.OpenAI")
def test_starter_prompt_success(mock_openai_class, dummy_config):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"prompts": ["Custom Q1?", "Custom Q2?"]}'
    mock_client.chat.completions.create.return_value = mock_response
    
    service = StarterPromptService(dummy_config)
    dossier = PersonaDossier(
        figure_id="test", name="T", era="E", identity="I", worldview=[], speech_style=[],
        temperament=[], core_topics=[], knowledge_boundary=[], posthumous_policy="P",
        taboo_or_uncertain_topics=[], example_phrases=[], evidence_snippets=[]
    )
    
    prompts = service.generate_starter_prompts(dossier, count=2)
    assert len(prompts) == 2
    assert "Custom Q1?" in prompts
