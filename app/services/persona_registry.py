from __future__ import annotations

import json
from pathlib import Path
import re

from app.models.schemas import PersonaDossier
from app.services.persona_loader import PersonaLoader, PersonaLoaderError


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
_CUSTOM_SUFFIX_PATTERN = re.compile(r"^(?P<root>.+?)_custom(?:_(?P<index>\d+))?$")


def slugify(value: str) -> str:
    """
    Normalize user- or model-provided ids into filesystem-safe figure ids.
    """
    normalized = _SLUG_PATTERN.sub("_", value.strip().lower()).strip("_")
    return normalized or "custom_figure"


class PersonaRegistry:
    """
    Manages loading and saving of both preset and custom personas.
    Provides a unified view of all available figures.
    """

    def __init__(self, preset_dir: str | Path, custom_dir: str | Path) -> None:
        self.preset_dir = Path(preset_dir)
        self.custom_dir = Path(custom_dir)

        # Ensure custom dir exists
        self.custom_dir.mkdir(parents=True, exist_ok=True)

        self.preset_loader = PersonaLoader(self.preset_dir)
        self.custom_loader = PersonaLoader(self.custom_dir)

    def list_preset_figures(self) -> list[str]:
        """
        Return preset figure ids in stable order.
        """
        return self.preset_loader.list_available_figures()

    def list_custom_figures(self) -> list[str]:
        """
        Return custom figure ids in stable order.
        """
        return self.custom_loader.list_available_figures()

    def list_available_figures(self) -> list[str]:
        """
        Return all available figure ids with presets first and customs after.
        """
        presets = self.list_preset_figures()
        preset_ids = set(presets)
        customs = [figure_id for figure_id in self.list_custom_figures() if figure_id not in preset_ids]
        return presets + customs

    def is_custom(self, figure_id: str) -> bool:
        """
        Return whether the figure id is backed by custom storage.
        """
        return self.custom_loader.exists(slugify(figure_id))

    def load(self, figure_id: str) -> PersonaDossier:
        """
        Load a persona dossier. Custom figures take precedence over presets if they share an id.
        """
        normalized_figure_id = slugify(figure_id)

        if self.custom_loader.exists(normalized_figure_id):
            return self.custom_loader.load(normalized_figure_id)
        if self.preset_loader.exists(normalized_figure_id):
            return self.preset_loader.load(normalized_figure_id)

        raise PersonaLoaderError(f"Persona file not found for '{figure_id}' in presets or custom storage.")

    def reserve_custom_figure_id(self, figure_id: str) -> str:
        """
        Return a readable, collision-free custom figure id.
        """
        base_figure_id = slugify(figure_id)
        if not self._figure_id_in_use(base_figure_id):
            return base_figure_id

        candidate_root = self._build_custom_collision_root(base_figure_id)
        candidate = candidate_root
        suffix = 2
        while self._figure_id_in_use(candidate):
            candidate = f"{candidate_root}_{suffix}"
            suffix += 1

        return candidate

    def save_custom_persona(
        self,
        dossier: PersonaDossier,
        *,
        overwrite: bool = False,
    ) -> PersonaDossier:
        """
        Save a generated persona to the custom personas directory.
        """
        normalized_dossier = self._normalize_dossier(dossier)
        self._validate_custom_save(normalized_dossier.figure_id, overwrite=overwrite)

        try:
            self._write_custom_file(normalized_dossier)
        except OSError as exc:
            raise PersonaLoaderError(
                f"Could not save custom persona: {normalized_dossier.figure_id}.json"
            ) from exc

        return normalized_dossier

    def update_custom_persona(
        self,
        original_figure_id: str,
        dossier: PersonaDossier,
    ) -> PersonaDossier:
        """
        Replace or rename an existing custom persona while preserving preset safety.
        """
        original_id = slugify(original_figure_id)
        if not self.custom_loader.exists(original_id):
            raise PersonaLoaderError(
                f"Cannot edit '{original_figure_id}' because it is not a saved custom figure."
            )

        normalized_dossier = self._normalize_dossier(dossier)
        if normalized_dossier.figure_id == original_id:
            return self.save_custom_persona(normalized_dossier, overwrite=True)

        self._validate_custom_save(normalized_dossier.figure_id, overwrite=False)
        try:
            self._write_custom_file(normalized_dossier)
        except OSError as exc:
            raise PersonaLoaderError(
                f"Could not save custom persona: {normalized_dossier.figure_id}.json"
            ) from exc

        try:
            self._delete_custom_file(original_id)
        except PersonaLoaderError:
            try:
                self._delete_custom_file(normalized_dossier.figure_id)
            except PersonaLoaderError:
                pass
            raise

        return normalized_dossier

    def delete_custom_persona(self, figure_id: str) -> None:
        """
        Delete a saved custom persona. Presets remain read-only.
        """
        normalized_figure_id = slugify(figure_id)
        if self.preset_loader.exists(normalized_figure_id):
            raise PersonaLoaderError(
                f"Cannot delete preset figure '{normalized_figure_id}'. Presets are read-only."
            )
        self._delete_custom_file(normalized_figure_id)

    def _normalize_dossier(self, dossier: PersonaDossier) -> PersonaDossier:
        normalized_figure_id = slugify(dossier.figure_id or dossier.name)
        return dossier.model_copy(update={"figure_id": normalized_figure_id})

    def _validate_custom_save(self, figure_id: str, *, overwrite: bool) -> None:
        if self.preset_loader.exists(figure_id):
            raise PersonaLoaderError(
                f"Cannot save custom persona '{figure_id}' because it would overwrite a preset figure."
            )

        if self.custom_loader.exists(figure_id) and not overwrite:
            raise PersonaLoaderError(
                f"Custom persona '{figure_id}' already exists. Choose another id or save with overwrite=True."
            )

    def _figure_id_in_use(self, figure_id: str) -> bool:
        return self.custom_loader.exists(figure_id) or self.preset_loader.exists(figure_id)

    def _build_custom_collision_root(self, base_figure_id: str) -> str:
        match = _CUSTOM_SUFFIX_PATTERN.match(base_figure_id)
        if match:
            return f"{match.group('root')}_custom"
        return f"{base_figure_id}_custom"

    def _write_custom_file(self, dossier: PersonaDossier) -> None:
        file_path = self.custom_dir / f"{dossier.figure_id}.json"
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(dossier.model_dump(exclude_none=True), file, indent=2, ensure_ascii=False)

    def _delete_custom_file(self, figure_id: str) -> None:
        file_path = self.custom_dir / f"{figure_id}.json"
        if not file_path.exists():
            raise PersonaLoaderError(
                f"Custom persona file not found for '{figure_id}'."
            )

        try:
            file_path.unlink()
        except OSError as exc:
            raise PersonaLoaderError(
                f"Could not delete custom persona: {file_path.name}"
            ) from exc
