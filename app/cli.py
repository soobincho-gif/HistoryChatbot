from __future__ import annotations

import uuid

from app.config import ConfigError, load_config
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoader, PersonaLoaderError
from app.services.question_classifier import QuestionClassifier
from app.services.response_generator import (
    OpenAIResponseGenerator,
    ResponseGenerationError,
)
from app.services.response_planner import ResponsePlanner
from app.services.simple_verifier import SimpleVerifier


EXIT_COMMANDS = {"exit", "quit", "q"}


def run_cli() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"[Config Error] {exc}")
        return

    persona_loader = PersonaLoader("app/personas")
    figures = persona_loader.list_available_figures()

    if not figures:
        print("No persona files found in app/personas.")
        return

    print("=" * 60)
    print("Historical Figure Chatbot")
    print("=" * 60)
    print("Available figures:")
    for idx, figure in enumerate(figures, start=1):
        print(f"{idx}. {figure}")

    selected_figure = _select_figure(figures)
    if selected_figure is None:
        print("No valid figure selected. Exiting.")
        return

    session_id = str(uuid.uuid4())

    memory_service = MemoryService()
    question_classifier = QuestionClassifier()
    response_planner = ResponsePlanner()
    response_generator = OpenAIResponseGenerator(config=config)
    response_verifier = SimpleVerifier()

    chat_service = ChatService(
        persona_loader=persona_loader,
        memory_service=memory_service,
        question_classifier=question_classifier,
        response_planner=response_planner,
        response_generator=response_generator,
        response_verifier=response_verifier,
    )

    try:
        dossier = persona_loader.load(selected_figure)
    except PersonaLoaderError as exc:
        print(f"[Persona Error] {exc}")
        return

    chat_service.start_session(session_id=session_id, figure_id=selected_figure)

    print("\n" + "-" * 60)
    print(f"You are now speaking with: {dossier.name}")
    print("Type your question and press Enter.")
    print(f"Type one of {sorted(EXIT_COMMANDS)} to leave.")
    print("-" * 60)

    while True:
        try:
            user_question = input("\nYou: ").strip()
        except EOFError:
            print("\nGoodbye.")
            break
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

        if not user_question:
            print("Please enter a question.")
            continue

        if user_question.lower() in EXIT_COMMANDS:
            print("Goodbye.")
            break

        try:
            pipeline_result = chat_service.chat(
                session_id=session_id,
                figure_id=selected_figure,
                user_question=user_question,
            )
        except (PersonaLoaderError, ResponseGenerationError, ValueError, KeyError) as exc:
            print(f"\n[Error] {exc}")
            continue

        print(f"\n{dossier.name}: {pipeline_result.final_answer}")

        if config.debug:
            print("\n[DEBUG] classification =", pipeline_result.classification.model_dump())
            print("[DEBUG] response_plan =", pipeline_result.response_plan.model_dump())


def _select_figure(figures: list[str]) -> str | None:
    raw = input("\nChoose a figure by number or id: ").strip().lower()

    if raw in figures:
        return raw

    if raw.isdigit():
        idx = int(raw)
        if 1 <= idx <= len(figures):
            return figures[idx - 1]

    return None


def main() -> None:
    """Compatibility wrapper for the CLI entrypoint."""

    run_cli()
