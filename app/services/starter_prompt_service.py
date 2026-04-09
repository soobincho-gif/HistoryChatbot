from __future__ import annotations

import json
from openai import OpenAI

from app.config import AppConfig
from app.models.schemas import PersonaDossier

class StarterPromptGenerationError(Exception):
    """Raised when starter prompt generation fails."""

class StarterPromptService:
    """
    Generates compelling starter prompts based on a provided PersonaDossier.
    """

    def __init__(self, config: AppConfig) -> None:
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model

    def generate_starter_prompts(self, dossier: PersonaDossier, count: int = 4) -> list[str]:
        """
        Produce a list of starter questions for the given persona.
        """
        system_prompt = (
            "You are an expert conversational architect for a Historical Salon Chatbot. "
            f"Your task is to generate {count} intriguing, thought-provoking questions that a user could ask "
            "this specific historical figure to begin a deep conversation. "
            "Output strictly valid JSON in the format:\n"
            '{ "prompts": ["question 1?", "question 2?", ...] }'
        )

        dossier_json = dossier.model_dump_json(exclude={"starter_prompts"})
        user_prompt = f"Please generate starter prompts based on this persona:\n{dossier_json}"

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
            
            prompts = parsed_data.get("prompts", [])
            
            # fallback if it's empty
            if not prompts:
                return [
                    "What advice would you give to modern society?",
                    "What was your greatest challenge?",
                    "How do you wish to be remembered?"
                ]
            
            return prompts[:count]
        except Exception as exc:
            raise StarterPromptGenerationError(f"Failed to generate starter prompts: {exc}") from exc
