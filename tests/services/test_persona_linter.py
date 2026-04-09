from app.services.persona_linter import PersonaLinter
from app.models.schemas import PersonaDossier

def test_persona_linter_empty():
    dossier = PersonaDossier(
        figure_id="test",
        name="Test",
        era="Test",
        identity="Test",
        worldview=[],
        speech_style=[],
        temperament=[],
        core_topics=[],
        knowledge_boundary=[],
        posthumous_policy="",
        taboo_or_uncertain_topics=[],
        example_phrases=[],
        evidence_snippets=[]
    )
    
    linter = PersonaLinter()
    warnings = linter.lint(dossier)
    
    categories = [w.category for w in warnings]
    assert "Grounding" in categories
    assert "Chronology" in categories
    assert "Policy" in categories
    assert "Depth" in categories

def test_persona_linter_pass():
    dossier = PersonaDossier(
        figure_id="test",
        name="Test",
        era="Test",
        birth_year=1900,
        death_year=1980,
        identity="Test",
        worldview=["W1", "W2"],
        speech_style=["S1", "S2"],
        temperament=["T1"],
        core_topics=["C1", "C2", "C3"],
        knowledge_boundary=[],
        posthumous_policy="Act and speak as if you are bound by your lifetime.",
        taboo_or_uncertain_topics=[],
        example_phrases=[],
        evidence_snippets=[{"topic": "S1", "content": "C1"}, {"topic": "S2", "content": "C2"}]
    )
    linter = PersonaLinter()
    warnings = linter.lint(dossier)
    assert len(warnings) == 0
