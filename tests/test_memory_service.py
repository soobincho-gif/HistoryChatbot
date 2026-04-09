from app.services.memory_service import MemoryConfig, MemoryService


def test_memory_service_creates_and_updates_session() -> None:
    service = MemoryService()
    service.create_session(session_id="s1", figure_id="einstein")

    service.add_user_turn("s1", "What is time?")
    service.add_assistant_turn("s1", "Time is not as absolute as common sense suggests.")

    memory = service.get_session("s1")
    assert memory.figure_id == "einstein"
    assert len(memory.recent_turns) == 2
    assert memory.recent_turns[0].role == "user"
    assert memory.recent_turns[1].role == "assistant"


def test_memory_service_trims_turns_and_builds_summary() -> None:
    service = MemoryService(
        MemoryConfig(max_recent_turns=4, summary_trigger_turn_count=4, max_summary_chars=500)
    )
    service.create_session(session_id="s2", figure_id="gandhi")

    service.add_user_turn("s2", "What is truth?")
    service.add_assistant_turn("s2", "Truth demands discipline.")
    service.add_user_turn("s2", "And what of violence?")
    service.add_assistant_turn("s2", "Violence wounds both the victim and the soul.")
    service.add_user_turn("s2", "What about resistance?")

    memory = service.get_session("s2")

    assert len(memory.recent_turns) == 4
    assert memory.recent_turns[0].content == "Truth demands discipline."
    assert "Assistant replied" in memory.session_summary


def test_memory_service_updates_preferences_with_validation() -> None:
    service = MemoryService()
    service.create_session(session_id="s3", figure_id="cleopatra")

    memory = service.update_preferences(
        "s3",
        preferred_answer_length="short",
        wants_simple_explanations=False,
        prefers_more_historical_detail=True,
    )

    assert memory.user_preferences.preferred_answer_length == "short"
    assert memory.user_preferences.wants_simple_explanations is False
    assert memory.user_preferences.prefers_more_historical_detail is True
