from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from app.models.schemas import PersonaDossier


class PersonaLoaderError(Exception):
    """Raised when persona data cannot be loaded or validated."""


class PersonaLoader:
    """
    Loads historical figure persona dossiers from JSON files and validates them
    against the PersonaDossier schema.
    """

    def __init__(self, persona_dir: str | Path) -> None:
        self.persona_dir = Path(persona_dir)

    def _build_path(self, figure_id: str) -> Path:
        return self.persona_dir / f"{figure_id}.json"

    def list_available_figures(self) -> list[str]:
        """
        Return all available figure ids based on *.json files in the persona dir.
        """
        if not self.persona_dir.exists():
            return []

        return sorted(path.stem for path in self.persona_dir.glob("*.json"))

    def exists(self, figure_id: str) -> bool:
        """
        Check whether a persona JSON file exists for the given figure id.
        """
        return self._build_path(figure_id).exists()

    def load(self, figure_id: str) -> PersonaDossier:
        """
        Load and validate a persona dossier by figure id.
        """
        file_path = self._build_path(figure_id)

        if not file_path.exists():
            available = ", ".join(self.list_available_figures()) or "none"
            raise PersonaLoaderError(
                f"Persona file not found for '{figure_id}'. Available figures: {available}"
            )

        try:
            with file_path.open("r", encoding="utf-8") as file:
                raw_data = json.load(file)
        except json.JSONDecodeError as exc:
            raise PersonaLoaderError(
                f"Invalid JSON in persona file: {file_path.name}"
            ) from exc
        except OSError as exc:
            raise PersonaLoaderError(
                f"Could not read persona file: {file_path.name}"
            ) from exc

        try:
            dossier = PersonaDossier.model_validate(raw_data)
        except ValidationError as exc:
            raise PersonaLoaderError(
                f"Persona file failed schema validation: {file_path.name}"
            ) from exc

        if dossier.figure_id != figure_id:
            raise PersonaLoaderError(
                f"Persona file mismatch: requested '{figure_id}' "
                f"but dossier.figure_id is '{dossier.figure_id}'."
            )

        return dossier
