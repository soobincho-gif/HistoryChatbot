from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from app.models.schemas import ChatTurn, SessionMemory, UserPreferences


@dataclass(slots=True)
class MemoryConfig:
    """
    Config for short-term memory behavior.
    """

    max_recent_turns: int = 10
    summary_trigger_turn_count: int = 8
    max_summary_chars: int = 500


class MemoryService:
    """
    In-memory session manager for multi-turn chat.

    Responsibilities:
    - create session memory
    - append user/assistant turns
    - trim recent turns
    - update a lightweight session summary
    - preserve user preferences
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        self.config = config or MemoryConfig()
        self._sessions: dict[str, SessionMemory] = {}

    def create_session(
        self,
        session_id: str,
        figure_id: str,
        user_preferences: UserPreferences | None = None,
    ) -> SessionMemory:
        """
        Create a new session or overwrite an existing one with a clean state.
        """
        memory = SessionMemory(
            session_id=session_id,
            figure_id=figure_id,
            recent_turns=[],
            session_summary="",
            user_preferences=user_preferences or UserPreferences(),
        )
        self._sessions[session_id] = memory
        return memory

    def has_session(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_session(self, session_id: str) -> SessionMemory:
        """
        Return a session memory object. Raise KeyError if missing.
        """
        return self._sessions[session_id]

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def update_preferences(
        self,
        session_id: str,
        *,
        preferred_answer_length: str | None = None,
        wants_simple_explanations: bool | None = None,
        prefers_more_historical_detail: bool | None = None,
    ) -> SessionMemory:
        """
        Update user preferences for an existing session.
        """
        memory = self.get_session(session_id)
        current_data = memory.user_preferences.model_dump()

        if preferred_answer_length is not None:
            current_data["preferred_answer_length"] = preferred_answer_length
        if wants_simple_explanations is not None:
            current_data["wants_simple_explanations"] = wants_simple_explanations
        if prefers_more_historical_detail is not None:
            current_data["prefers_more_historical_detail"] = prefers_more_historical_detail

        memory.user_preferences = UserPreferences.model_validate(current_data)
        return memory

    def add_user_turn(self, session_id: str, content: str) -> SessionMemory:
        return self._add_turn(session_id, role="user", content=content)

    def add_assistant_turn(self, session_id: str, content: str) -> SessionMemory:
        return self._add_turn(session_id, role="assistant", content=content)

    def add_system_turn(self, session_id: str, content: str) -> SessionMemory:
        return self._add_turn(session_id, role="system", content=content)

    def _add_turn(
        self,
        session_id: str,
        *,
        role: Literal["system", "user", "assistant"],
        content: str,
    ) -> SessionMemory:
        """
        Add a turn, trim old turns if needed, and refresh summary when useful.
        """
        memory = self.get_session(session_id)
        memory.recent_turns.append(ChatTurn(role=role, content=content.strip()))
        self._trim_recent_turns(memory)
        self._maybe_refresh_summary(memory)
        return memory

    def get_recent_turns(self, session_id: str) -> list[ChatTurn]:
        return list(self.get_session(session_id).recent_turns)

    def get_recent_turns_as_messages(self, session_id: str) -> list[dict[str, str]]:
        """
        Convert recent turns into a model-friendly messages format.
        Useful later for prompt assembly.
        """
        memory = self.get_session(session_id)
        return [{"role": turn.role, "content": turn.content} for turn in memory.recent_turns]

    def get_context_bundle(self, session_id: str) -> dict[str, object]:
        """
        Convenience method for downstream planner/generator services.
        """
        memory = self.get_session(session_id)
        return {
            "session_id": memory.session_id,
            "figure_id": memory.figure_id,
            "session_summary": memory.session_summary,
            "recent_turns": self.get_recent_turns_as_messages(session_id),
            "user_preferences": memory.user_preferences.model_dump(),
        }

    def _trim_recent_turns(self, memory: SessionMemory) -> None:
        """
        Keep only the most recent N turns.
        """
        max_turns = self.config.max_recent_turns
        if len(memory.recent_turns) > max_turns:
            memory.recent_turns = memory.recent_turns[-max_turns:]

    def _maybe_refresh_summary(self, memory: SessionMemory) -> None:
        """
        Refresh the short session summary when enough dialogue has accumulated.

        This is intentionally simple for MVP:
        - extract only user/assistant turns
        - keep the latest few meaningful lines
        - compress into a short plain-text summary

        Later, this can be replaced with an LLM summary step.
        """
        conversational_turns = [
            turn for turn in memory.recent_turns if turn.role in {"user", "assistant"}
        ]

        if len(conversational_turns) < self.config.summary_trigger_turn_count:
            return

        summary = self._build_lightweight_summary(conversational_turns)
        memory.session_summary = summary[: self.config.max_summary_chars]

    def _build_lightweight_summary(self, turns: Iterable[ChatTurn]) -> str:
        """
        Very simple heuristic summary for MVP.

        Example output:
        'User asked: What is time? | Assistant replied: Time is not absolute.'
        """
        compact_lines: list[str] = []

        for turn in turns:
            cleaned = " ".join(turn.content.split())
            if len(cleaned) > 120:
                cleaned = cleaned[:117] + "..."
            prefix = "User asked" if turn.role == "user" else "Assistant replied"
            compact_lines.append(f"{prefix}: {cleaned}")

        if not compact_lines:
            return ""

        tail = compact_lines[-4:]
        return " | ".join(tail)
