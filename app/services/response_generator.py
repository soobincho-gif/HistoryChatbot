from __future__ import annotations

from openai import OpenAI

from app.config import AppConfig
from app.models.schemas import PersonaDossier, ResponsePlan, SessionMemory
from app.prompts.system_prompts import (
    build_character_instructions,
    build_generation_input,
)


class ResponseGenerationError(Exception):
    """Raised when final answer generation fails."""


class OpenAIResponseGenerator:
    """
    Final natural-language generator using the OpenAI Responses API.

    This class is intentionally narrow:
    - build instructions
    - build input payload
    - call model
    - extract final text
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)

    def generate(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        response_plan: ResponsePlan,
    ) -> str:
        instructions = build_character_instructions(
            dossier=dossier,
            response_plan=response_plan,
        )
        rendered_input = build_generation_input(
            user_question=user_question,
            dossier=dossier,
            memory=memory,
        )

        try:
            response = self.client.responses.create(
                model=self.config.openai_model,
                instructions=instructions,
                input=rendered_input,
            )
        except Exception as exc:
            raise ResponseGenerationError(
                f"OpenAI response generation failed: {exc}"
            ) from exc

        final_text = getattr(response, "output_text", None)
        if isinstance(final_text, str) and final_text.strip():
            return final_text.strip()

        fallback_text = self._extract_text_fallback(response)
        if fallback_text:
            return fallback_text

        raise ResponseGenerationError(
            "The model returned no readable text output."
        )

    def _extract_text_fallback(self, response: object) -> str:
        """
        Defensive fallback parser.
        The SDK exposes `output_text`, which should usually be enough.
        This method only exists to reduce brittleness.
        """
        output = getattr(response, "output", None)
        if not output:
            return ""

        fragments: list[str] = []

        for item in output:
            content = getattr(item, "content", None)
            if content is None and isinstance(item, dict):
                content = item.get("content")
            if not content:
                continue
            for part in content:
                text = getattr(part, "text", None)
                if text is None and isinstance(part, dict):
                    text = part.get("text")
                if text:
                    fragments.append(str(text))

        return "\n".join(fragment.strip() for fragment in fragments if fragment.strip()).strip()
