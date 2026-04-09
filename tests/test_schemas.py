"""Schema and persona fixture tests."""

import json
from pathlib import Path

from app.models import (
    ChatPipelineResult,
    ChatTurn,
    EvidenceSnippet,
    PersonaDossier,
    QuestionClassification,
    ResponsePlan,
    SessionMemory,
    VerifierIssue,
    VerifierResult,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PERSONA_DIR = PROJECT_ROOT / "app" / "personas"


def test_persona_dossier_accepts_required_fields() -> None:
    dossier = PersonaDossier(
        figure_id="einstein",
        name="Albert Einstein",
        era="Late 19th to mid-20th century Europe and America",
        birth_year=1879,
        death_year=1955,
        identity="A theoretical physicist known for relativity.",
        worldview=["Curiosity matters."],
        speech_style=["Thoughtful"],
        temperament=["Patient"],
        core_topics=["Physics"],
        knowledge_boundary=["He should not claim direct knowledge of events after 1955."],
        posthumous_policy="Respond from principle and acknowledge the time gap.",
        taboo_or_uncertain_topics=["Detailed modern policy claims"],
        example_phrases=["From the standpoint of reason, one must ask..."],
        evidence_snippets=[
            EvidenceSnippet(
                topic="science",
                content="Einstein is associated with relativity and theoretical reasoning.",
                source_hint="scientific biography",
            )
        ],
    )

    assert dossier.figure_id == "einstein"
    assert dossier.evidence_snippets[0].topic == "science"


def test_session_memory_keeps_identity_and_preferences() -> None:
    memory = SessionMemory(
        session_id="session-1",
        figure_id="einstein",
        recent_turns=[ChatTurn(role="user", content="Explain relativity simply.")],
    )

    assert memory.figure_id == "einstein"
    assert memory.user_preferences.preferred_answer_length == "medium"
    assert memory.recent_turns[0].content == "Explain relativity simply."


def test_question_classification_and_response_plan_are_structured() -> None:
    classification = QuestionClassification(
        question_type="factual",
        requires_caution=False,
        is_posthumous=False,
        should_refuse_direct_claim=False,
        answer_mode="direct_in_character",
        reasoning_note="The question concerns a topic within the figure's lifetime expertise.",
    )
    plan = ResponsePlan(
        tone_strategy="Thoughtful, clear, and concept-driven.",
        historical_scope="Stay within Einstein's lifetime and speak from first principles.",
        mention_limits=False,
        key_points=["Explain the core concept simply."],
        avoid_claims=["Do not mention modern model names or products."],
        recommended_length="medium",
    )
    pipeline_result = ChatPipelineResult(
        classification=classification,
        response_plan=plan,
        final_answer="Relativity asks us to reconsider time and space together.",
    )

    assert pipeline_result.classification.question_type == "factual"
    assert pipeline_result.response_plan.recommended_length == "medium"


def test_verifier_result_supports_issue_details() -> None:
    result = VerifierResult(
        status="revise",
        issues=[
            VerifierIssue(
                issue_type="historical_overreach",
                description="The answer implies direct knowledge of modern AI systems.",
            )
        ],
        suggested_fix="Reframe the answer as inference from the figure's principles.",
    )

    assert result.status == "revise"
    assert result.issues[0].issue_type == "historical_overreach"


def test_persona_json_files_validate_against_schema() -> None:
    for persona_name in ("einstein", "gandhi", "cleopatra"):
        persona_path = PERSONA_DIR / f"{persona_name}.json"
        persona_data = json.loads(persona_path.read_text(encoding="utf-8"))
        dossier = PersonaDossier.model_validate(persona_data)

        assert dossier.figure_id == persona_name
        assert dossier.evidence_snippets
