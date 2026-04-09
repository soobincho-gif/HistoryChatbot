from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


QuestionType = Literal[
    "factual",
    "philosophical",
    "personal_life",
    "posthumous_current_events",
    "counterfactual",
    "ambiguous",
]

AnswerMode = Literal[
    "direct_in_character",
    "cautious_historical_projection",
    "reflective_opinion",
    "clarifying_question",
]

VerifierStatus = Literal[
    "pass",
    "revise",
    "fail_safe",
]


class EvidenceSnippet(BaseModel):
    """
    Short fact-grounding unit for a historical figure.
    Not a full citation engine yet, but enough for controlled grounding.
    """

    topic: str = Field(..., description="Topic label for the evidence snippet")
    content: str = Field(..., description="Short grounding text")
    source_hint: Optional[str] = Field(
        default=None,
        description="Human-readable source hint, e.g. biography, speech, letter",
    )


class PersonaDossier(BaseModel):
    """
    Structured definition of a historical figure.
    Style and facts are both represented, but in clearly separated fields.
    """

    figure_id: str = Field(..., description="Unique id, e.g. einstein")
    name: str
    era: str
    birth_year: Optional[int] = None
    death_year: Optional[int] = None

    identity: str = Field(..., description="Who this person is in one or two lines")
    worldview: List[str] = Field(
        default_factory=list,
        description="Core beliefs, values, and recurring themes",
    )
    speech_style: List[str] = Field(
        default_factory=list,
        description="How the figure tends to speak",
    )
    temperament: List[str] = Field(
        default_factory=list,
        description="Emotional and interpersonal tone",
    )

    core_topics: List[str] = Field(
        default_factory=list,
        description="Topics the figure can speak about strongly",
    )
    knowledge_boundary: List[str] = Field(
        default_factory=list,
        description="Limits of what the figure can plausibly know directly",
    )
    posthumous_policy: str = Field(
        ...,
        description="How to answer questions about events after the figure's lifetime",
    )
    taboo_or_uncertain_topics: List[str] = Field(
        default_factory=list,
        description="Sensitive, uncertain, or ambiguous areas requiring caution",
    )

    example_phrases: List[str] = Field(
        default_factory=list,
        description="Short example expressions to anchor tone",
    )
    evidence_snippets: List[EvidenceSnippet] = Field(
        default_factory=list,
        description="Short grounding snippets for controlled historical plausibility",
    )
    starter_prompts: List[str] = Field(
        default_factory=list,
        description="Generated starter prompts to help users initiate chat",
    )


class ChatTurn(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class UserPreferences(BaseModel):
    preferred_answer_length: Literal["short", "medium", "long"] = "medium"
    wants_simple_explanations: bool = True
    prefers_more_historical_detail: bool = False


class SessionMemory(BaseModel):
    """
    Memory that supports multi-turn continuity.
    recent_turns = raw local context
    session_summary = compact compressed memory
    user_preferences = style preferences
    """

    session_id: str
    figure_id: str
    recent_turns: List[ChatTurn] = Field(default_factory=list)
    session_summary: str = ""
    user_preferences: UserPreferences = Field(default_factory=UserPreferences)


class QuestionClassification(BaseModel):
    """
    Result of the analysis step before generation.
    """

    question_type: QuestionType
    requires_caution: bool
    is_posthumous: bool
    should_refuse_direct_claim: bool
    answer_mode: AnswerMode
    needs_clarification: bool = False
    reasoning_note: str = Field(
        ...,
        description="Short internal explanation for why the question was classified this way",
    )


class ResponsePlan(BaseModel):
    """
    Structured answer plan used before final response generation.
    """

    tone_strategy: str = Field(
        ...,
        description="How the response should sound",
    )
    historical_scope: str = Field(
        ...,
        description="How far the answer can go historically",
    )
    mention_limits: bool = Field(
        ...,
        description="Whether the answer should explicitly mention uncertainty or time-bound limits",
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Main content points to include",
    )
    avoid_claims: List[str] = Field(
        default_factory=list,
        description="Claims or tones to avoid",
    )
    recommended_length: Literal["short", "medium", "long"] = "medium"


class VerifierIssue(BaseModel):
    issue_type: Literal[
        "persona_drift",
        "historical_overreach",
        "anachronism",
        "non_answer",
        "continuity_problem",
        "overconfidence",
        "generic_tone",
    ]
    description: str


class VerifierResult(BaseModel):
    status: VerifierStatus
    issues: List[VerifierIssue] = Field(default_factory=list)
    suggested_fix: Optional[str] = None


class ChatPipelineResult(BaseModel):
    """
    Optional convenience object for debugging and later UI/logging.
    """

    classification: QuestionClassification
    response_plan: ResponsePlan
    final_answer: str
    verifier_result: Optional[VerifierResult] = None
