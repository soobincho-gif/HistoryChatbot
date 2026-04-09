from __future__ import annotations

import json
from openai import OpenAI

from app.config import AppConfig
from app.models.schemas import PersonaDossier, EvidenceSnippet
from app.services.persona_registry import slugify


class PersonaGenerationError(Exception):
    """Raised when persona generation fails."""


class PersonaBuilderService:
    """
    Generates a structured PersonaDossier for a custom historical figure.
    """

    def __init__(self, config: AppConfig) -> None:
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model

    def build_persona(
        self,
        name: str,
        era: str = "",
        known_for: str = "",
        tone_hint: str = "",
    ) -> PersonaDossier:
        """
        Generate a PersonaDossier and starter prompts using the LLM.
        """
        fallback_figure_id = slugify(name)
        
        system_prompt = (
            "You are an expert historian and persona architect for a Historical Salon Chatbot.\n"
            "Your task is to create a detailed, highly structured persona dossier in JSON format.\n\n"
            "The JSON must EXACTLY match the following schema structure, with no markdown wrappers if possible (or just valid JSON):\n"
            "{\n"
            '  "figure_id": "string",\n'
            '  "name": "string",\n'
            '  "era": "string",\n'
            '  "birth_year": number or null,\n'
            '  "death_year": number or null,\n'
            '  "identity": "string (1-2 sentences)",\n'
            '  "worldview": ["string", ...],\n'
            '  "speech_style": ["string", ...],\n'
            '  "temperament": ["string", ...],\n'
            '  "core_topics": ["string", ...],\n'
            '  "knowledge_boundary": ["string", ...],\n'
            '  "posthumous_policy": "string",\n'
            '  "taboo_or_uncertain_topics": ["string", ...],\n'
            '  "example_phrases": ["string", ...],\n'
            '  "evidence_snippets": [\n'
            '     {"topic": "string", "content": "string", "source_hint": "string"}\n'
            "  ],\n"
            '  "starter_prompts": ["string (3-5 intriguing questions to ask them)"]\n'
            "}\n\n"
            "RULES:\n"
            "- 'figure_id' must be closely related to the name (e.g. 'marcus_aurelius').\n"
            "- 'worldview', 'speech_style', 'temperament', 'core_topics', 'knowledge_boundary', 'taboo_or_uncertain_topics', 'example_phrases' should be arrays of short strings.\n"
            "- 'evidence_snippets' must contain 3-4 historical facts grounding the persona.\n"
            "- 'starter_prompts' should be exactly 3 to 5 questions users can ask this figure to start a compelling conversation.\n"
        )
        
        user_prompt = f"Please generate a persona for the historical figure: {name}.\n"
        if era:
            user_prompt += f"Era / Region / Context: {era}\n"
        if known_for:
            user_prompt += f"Known for: {known_for}\n"
        if tone_hint:
            user_prompt += f"Tone / Style Hint: {tone_hint}\n"
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            raw_content = response.choices[0].message.content or "{}"
            parsed_data = json.loads(raw_content)

            # Enforce a filesystem-safe figure id even if the model returns quirky text.
            parsed_data["figure_id"] = slugify(
                str(parsed_data.get("figure_id") or fallback_figure_id)
            )

            return PersonaDossier.model_validate(parsed_data)
        except Exception as exc:
            raise PersonaGenerationError(f"Failed to generate persona for {name}: {exc}") from exc
