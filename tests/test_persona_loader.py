from app.services.persona_loader import PersonaLoader


def test_persona_loader_can_list_and_load() -> None:
    loader = PersonaLoader("app/personas")

    figures = loader.list_available_figures()
    assert "einstein" in figures

    dossier = loader.load("einstein")
    assert dossier.figure_id == "einstein"
    assert dossier.name == "Albert Einstein"
