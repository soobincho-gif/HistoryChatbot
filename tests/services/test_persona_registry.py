import json

import pytest

from app.models.schemas import PersonaDossier
from app.services.persona_registry import PersonaLoaderError, PersonaRegistry, slugify


def _build_dossier(
    *,
    figure_id: str = "test_custom",
    name: str = "Custom Alice",
    identity: str = "I am custom",
    starter_prompts: list[str] | None = None,
) -> PersonaDossier:
    return PersonaDossier(
        figure_id=figure_id,
        name=name,
        era="Custom Era",
        identity=identity,
        worldview=["Analytical imagination", "Measured curiosity"],
        speech_style=["Reflective precision"],
        temperament=["Curious", "Calm"],
        core_topics=["Science", "Ethics"],
        knowledge_boundary=["No firsthand knowledge beyond lifetime"],
        posthumous_policy="Speak cautiously about events beyond my life.",
        taboo_or_uncertain_topics=["Private gossip"],
        example_phrases=["Let us examine the principle carefully."],
        evidence_snippets=[],
        starter_prompts=starter_prompts or ["Q1?"],
    )


@pytest.fixture
def temp_dirs(tmp_path):
    preset_dir = tmp_path / "presets"
    custom_dir = tmp_path / "customs"
    preset_dir.mkdir()
    custom_dir.mkdir()

    preset_dossier = {
        "figure_id": "test_preset",
        "name": "Preset Bob",
        "era": "Preset Era",
        "identity": "I am a preset",
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
    with (preset_dir / "test_preset.json").open("w", encoding="utf-8") as file:
        json.dump(preset_dossier, file)

    return preset_dir, custom_dir


def test_slugify_normalizes_ids() -> None:
    assert slugify(" Albert Einstein!! ") == "albert_einstein"
    assert slugify("___") == "custom_figure"


def test_registry_list_figures_keeps_presets_first(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)
    registry.save_custom_persona(_build_dossier(figure_id="aaa_custom"))

    assert registry.list_available_figures() == ["test_preset", "aaa_custom"]


def test_save_and_load_custom_slugifies_figure_id(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)

    saved = registry.save_custom_persona(
        _build_dossier(
            figure_id=" Test Custom!! ",
            name="Custom Alice",
        )
    )

    assert saved.figure_id == "test_custom"
    assert (custom_dir / "test_custom.json").exists()

    loaded = registry.load("Test Custom!!")
    assert loaded.name == "Custom Alice"
    assert registry.is_custom("test_custom") is True


def test_save_custom_persona_rejects_preset_collisions_even_with_overwrite(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)

    with pytest.raises(PersonaLoaderError, match="overwrite a preset figure"):
        registry.save_custom_persona(
            _build_dossier(figure_id="test_preset", name="Preset Shadow"),
        )

    with pytest.raises(PersonaLoaderError, match="overwrite a preset figure"):
        registry.save_custom_persona(
            _build_dossier(figure_id="test_preset", name="Preset Shadow"),
            overwrite=True,
        )


def test_reserve_custom_figure_id_adds_readable_suffixes(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)

    assert registry.reserve_custom_figure_id("test_preset") == "test_preset_custom"

    registry.save_custom_persona(_build_dossier(figure_id="test_preset_custom"))
    assert registry.reserve_custom_figure_id("test_preset") == "test_preset_custom_2"


def test_save_custom_persona_requires_explicit_overwrite_for_existing_custom(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)

    registry.save_custom_persona(_build_dossier(figure_id="test_custom", name="Custom Alice"))

    with pytest.raises(PersonaLoaderError, match="already exists"):
        registry.save_custom_persona(_build_dossier(figure_id="test_custom", name="New Alice"))

    registry.save_custom_persona(
        _build_dossier(figure_id="test_custom", name="New Alice"),
        overwrite=True,
    )

    loaded = registry.load("test_custom")
    assert loaded.name == "New Alice"


def test_update_and_delete_custom_persona_preserve_preset_safety(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)

    registry.save_custom_persona(_build_dossier(figure_id="history_hero"))
    updated = registry.update_custom_persona(
        "history_hero",
        _build_dossier(
            figure_id="History Hero Revised",
            name="History Hero Revised",
            starter_prompts=["What should people remember?"],
        ),
    )

    assert updated.figure_id == "history_hero_revised"
    assert registry.is_custom("history_hero_revised") is True
    assert (custom_dir / "history_hero.json").exists() is False

    with pytest.raises(PersonaLoaderError, match="not a saved custom figure"):
        registry.update_custom_persona(
            "test_preset",
            _build_dossier(figure_id="test_preset_clone"),
        )

    with pytest.raises(PersonaLoaderError, match="read-only"):
        registry.delete_custom_persona("test_preset")

    registry.delete_custom_persona("history_hero_revised")

    assert registry.is_custom("history_hero_revised") is False
    with pytest.raises(PersonaLoaderError):
        registry.load("history_hero_revised")


def test_registry_missing_figure(temp_dirs) -> None:
    preset_dir, custom_dir = temp_dirs
    registry = PersonaRegistry(preset_dir, custom_dir)

    with pytest.raises(PersonaLoaderError):
        registry.load("missing_figure")
