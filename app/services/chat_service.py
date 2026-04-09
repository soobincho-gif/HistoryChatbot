from __future__ import annotations

from typing import Protocol

from app.models.schemas import (
    ChatPipelineResult,
    PersonaDossier,
    ResponsePlan,
    SessionMemory,
)
from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoader
from app.services.question_classifier import QuestionClassifier
from app.services.response_planner import ResponsePlanner
from app.services.verifier import ResponseVerifier


class ResponseGenerator(Protocol):
    """
    Interface for final answer generation.
    Later this will be implemented with OpenAI Responses API.
    """

    def generate(
        self,
        *,
        user_question: str,
        dossier: PersonaDossier,
        memory: SessionMemory,
        response_plan: ResponsePlan,
    ) -> str:
        ...


class ChatService:
    """
    Thin orchestration layer for the historical figure chatbot pipeline.

    Pipeline:
    1. load persona
    2. get or create session
    3. add user turn
    4. classify question
    5. build response plan
    6. generate final answer
    7. optionally verify
    8. store assistant turn
    """

    def __init__(
        self,
        *,
        persona_loader: PersonaLoader,
        memory_service: MemoryService,
        question_classifier: QuestionClassifier,
        response_planner: ResponsePlanner,
        response_generator: ResponseGenerator,
        response_verifier: ResponseVerifier | None = None,
    ) -> None:
        self.persona_loader = persona_loader
        self.memory_service = memory_service
        self.question_classifier = question_classifier
        self.response_planner = response_planner
        self.response_generator = response_generator
        self.response_verifier = response_verifier

    def start_session(self, *, session_id: str, figure_id: str) -> SessionMemory:
        """
        Start a clean chat session for a selected historical figure.
        """
        return self.memory_service.create_session(
            session_id=session_id,
            figure_id=figure_id,
        )

    def chat(
        self,
        *,
        session_id: str,
        figure_id: str,
        user_question: str,
    ) -> ChatPipelineResult:
        dossier = self.persona_loader.load(figure_id)

        if not self.memory_service.has_session(session_id):
            self.memory_service.create_session(session_id=session_id, figure_id=figure_id)

        memory = self.memory_service.get_session(session_id)

        if memory.figure_id != figure_id:
            raise ValueError(
                f"Session figure mismatch: session is bound to '{memory.figure_id}', "
                f"but received '{figure_id}'."
            )

        self.memory_service.add_user_turn(session_id, user_question)
        updated_memory = self.memory_service.get_session(session_id)

        classification = self.question_classifier.classify(user_question, dossier)

        response_plan = self.response_planner.build_plan(
            user_question=user_question,
            dossier=dossier,
            memory=updated_memory,
            classification=classification,
        )

        final_answer = self.response_generator.generate(
            user_question=user_question,
            dossier=dossier,
            memory=updated_memory,
            response_plan=response_plan,
        )

        verifier_result = None
        if self.response_verifier is not None:
            verifier_result = self.response_verifier.verify(
                user_question=user_question,
                dossier=dossier,
                memory=updated_memory,
                draft_answer=final_answer,
            )

            if verifier_result.status == "fail_safe":
                final_answer = self._build_failsafe_answer(dossier)

        self.memory_service.add_assistant_turn(session_id, final_answer)

        return ChatPipelineResult(
            classification=classification,
            response_plan=response_plan,
            final_answer=final_answer,
            verifier_result=verifier_result,
        )

    def _build_failsafe_answer(self, dossier: PersonaDossier) -> str:
        """
        In-character safe fallback. Avoids generic 'as an AI model' language.
        """
        return (
            f"I would rather answer cautiously than pretend certainty. "
            f"From the perspective of {dossier.name}'s own time, I can offer only a limited judgment here."
        )
