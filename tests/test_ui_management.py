import os
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock

import json
from app.models.schemas import PersonaDossier

def test_manage_figure_flow(tmp_path):
    preset_dir = tmp_path / "presets"
    custom_dir = tmp_path / "customs"
    preset_dir.mkdir()
    custom_dir.mkdir()

    # Create a preset figure
    preset_dossier = PersonaDossier(
        figure_id="preset_ada", name="Preset Ada", era="Victorian", identity="Preset",
        worldview=[], speech_style=[], temperament=[], core_topics=[], knowledge_boundary=[],
        posthumous_policy="N/A", taboo_or_uncertain_topics=[], example_phrases=[],
        evidence_snippets=[], starter_prompts=[]
    )
    with (preset_dir / "preset_ada.json").open("w", encoding="utf-8") as f:
        json.dump(preset_dossier.model_dump(exclude_none=True), f)

    # Create a custom figure
    custom_dossier = PersonaDossier(
        figure_id="custom_bob", name="Custom Bob", era="Current", identity="Custom",
        worldview=[], speech_style=[], temperament=[], core_topics=[], knowledge_boundary=[],
        posthumous_policy="N/A", taboo_or_uncertain_topics=[], example_phrases=[],
        evidence_snippets=[], starter_prompts=[]
    )
    with (custom_dir / "custom_bob.json").open("w", encoding="utf-8") as f:
        json.dump(custom_dossier.model_dump(exclude_none=True), f)

    with patch("app.config.load_config") as mock_load_config:
        mock_config = MagicMock()
        mock_config.personas_dir = preset_dir
        mock_config.custom_personas_dir = custom_dir
        mock_load_config.return_value = mock_config

        ui_app_path = os.path.join(os.path.dirname(__file__), "../app/ui_streamlit.py")
        at = AppTest.from_file(ui_app_path).run()
        assert not at.exception

        # Select the custom figure
        at.sidebar.selectbox[0].set_value("custom_bob").run()
        
        # Check if the "Manage Figure" expander is rendered and click 'Edit Custom JSON'
        # To access expander, we look at at.sidebar
        # we can't easily query expanders but we can query buttons
        assert len(at.sidebar.button) > 0
        
        edit_btn = [btn for btn in at.sidebar.button if btn.label == "Edit Custom JSON"]
        assert len(edit_btn) == 1
        edit_btn[0].click().run()

        # Edit JSON logic
        # Text_area is now present due to dialog
        # Find the text area with the JSON
        assert len(at.text_area) > 0
        # set_value without .run() to avoid clearing dialog state
        new_json = at.text_area[0].value.replace("Custom Bob", "Custom Charles")
        at.text_area[0].set_value(new_json)

        # Click Save Changes
        all_btn_labels = [btn.label for btn in at.button]
        print(f"All buttons before save: {all_btn_labels}")
        save_btn = [btn for btn in at.button if btn.label == "Save Changes"]
        assert len(save_btn) == 1
        save_btn[0].click().run()
        
        all_btn_labels_after = [btn.label for btn in at.button]
        print(f"All buttons after save: {all_btn_labels_after}")

        # Now figure should be Custom Charles
        # Let's delete the custom figure
        del_btn = [btn for btn in at.sidebar.button if btn.label == "Delete Custom Figure"]
        assert len(del_btn) == 1
        del_btn[0].click().run()

        # After deletion, fallback occurs
        assert at.sidebar.selectbox[0].value == "preset_ada"
