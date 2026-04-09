from __future__ import annotations

import html
import json
import uuid

import streamlit as st
from pydantic import ValidationError

from app.config import ConfigError, load_config
from app.models.schemas import ChatPipelineResult, PersonaDossier
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService
from app.services.persona_loader import PersonaLoaderError
from app.services.persona_registry import PersonaRegistry
from app.services.persona_builder import PersonaBuilderService, PersonaGenerationError
from app.services.persona_linter import PersonaLinter
from app.services.starter_prompt_service import StarterPromptService
from app.services.question_classifier import QuestionClassifier
from app.services.response_generator import (
    OpenAIResponseGenerator,
    ResponseGenerationError,
)
from app.services.response_planner import ResponsePlanner
from app.services.simple_verifier import SimpleVerifier


FIGURE_PROMPTS = {
    "einstein": [
        "What matters more in discovery: logic or imagination?",
        "How should science handle moral responsibility?",
        "Would you trust modern AI without caution?",
    ],
    "gandhi": [
        "Can nonviolence still work in modern politics?",
        "What is the relationship between truth and power?",
        "How should a person resist injustice without hatred?",
    ],
    "cleopatra": [
        "What makes a leader durable under pressure?",
        "How do image and power work together?",
        "What should diplomacy achieve before force is used?",
    ],
}


st.set_page_config(
    page_title="Historical Figure Chatbot",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run_streamlit_app() -> None:
    _apply_global_styles()
    _render_shell()

    try:
        config = load_config()
    except ConfigError as exc:
        _render_setup_notice(str(exc))
        return

    persona_registry = PersonaRegistry(config.personas_dir, config.custom_personas_dir)
    figures = persona_registry.list_available_figures()
    if not figures:
        st.error("No persona files found in app/personas.")
        return

    _ensure_app_state(figures, config, persona_registry)
    chat_service = st.session_state.chat_service

    selected_figure = _render_sidebar(persona_registry, figures, chat_service, config)
    dossier = persona_registry.load(selected_figure)

    left_col, right_col = st.columns([1.75, 1.0], gap="large")

    with left_col:
        _render_hero(dossier.name)
        _render_chat_panel(dossier.name)

    with right_col:
        _render_right_rail(dossier)

    starter_prompt = _render_starter_prompts_at_bottom(dossier)
    submitted_prompt = st.chat_input(f"Ask {dossier.name} a question...")
    
    if starter_prompt:
        _process_question(chat_service, selected_figure, starter_prompt)
        st.rerun()
    if submitted_prompt:
        _process_question(chat_service, selected_figure, submitted_prompt)
        st.rerun()


def _ensure_app_state(figures: list[str], config, persona_registry: PersonaRegistry) -> None:
    if "selected_figure" not in st.session_state or st.session_state.selected_figure not in figures:
        st.session_state.selected_figure = figures[0]
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "transcript" not in st.session_state:
        st.session_state.transcript = []
    if "latest_pipeline_result" not in st.session_state:
        st.session_state.latest_pipeline_result = None
    if "chat_service" not in st.session_state:
        st.session_state.chat_service = ChatService(
            persona_loader=persona_registry,
            memory_service=MemoryService(),
            question_classifier=QuestionClassifier(),
            response_planner=ResponsePlanner(),
            response_generator=OpenAIResponseGenerator(config=config),
            response_verifier=SimpleVerifier(),
        )
        st.session_state.chat_service.start_session(
            session_id=st.session_state.session_id,
            figure_id=st.session_state.selected_figure,
        )
    elif not st.session_state.chat_service.memory_service.has_session(st.session_state.session_id):
        st.session_state.chat_service.start_session(
            session_id=st.session_state.session_id,
            figure_id=st.session_state.selected_figure,
        )


def _apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
            --paper: #f5f1e8;
            --paper-soft: #fbf8f1;
            --ink: #1e1914;
            --ink-muted: #685c50;
            --accent: #b85b37;
            --accent-deep: #8f4328;
            --olive: #6f7565;
            --gold: #c9a55b;
            --line: rgba(39, 28, 21, 0.12);
            --card: rgba(255, 252, 245, 0.82);
            --shadow: 0 18px 50px rgba(53, 37, 27, 0.08);
            --radius-lg: 24px;
            --radius-md: 16px;
            --radius-sm: 12px;
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(184, 91, 55, 0.14), transparent 28%),
                radial-gradient(circle at top right, rgba(111, 117, 101, 0.12), transparent 26%),
                linear-gradient(180deg, #f8f4ec 0%, #f2ecdf 100%);
            color: var(--ink);
        }

        [data-testid="stSidebar"] {
            background: rgba(252, 248, 241, 0.86);
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.2rem;
        }

        h1, h2, h3, h4 {
            font-family: 'Cormorant Garamond', serif !important;
            color: var(--ink);
            letter-spacing: -0.02em;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1240px;
        }

        .salon-shell {
            background: rgba(255, 252, 245, 0.74);
            border: 1px solid var(--line);
            border-radius: 28px;
            box-shadow: var(--shadow);
            padding: 1.1rem 1.2rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(8px);
        }

        .salon-kicker {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--olive);
        }

        .hero-card {
            border: 1px solid var(--line);
            background:
                linear-gradient(135deg, rgba(255,255,255,0.68), rgba(255,248,239,0.88)),
                linear-gradient(180deg, rgba(184, 91, 55, 0.05), rgba(111, 117, 101, 0.05));
            border-radius: 30px;
            padding: 2rem 2rem 1.8rem 2rem;
            box-shadow: var(--shadow);
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(2.5rem, 5vw, 4.5rem);
            line-height: 0.95;
            margin: 0.35rem 0 0.8rem 0;
            color: var(--ink);
        }

        .hero-subtitle {
            font-size: 1.02rem;
            line-height: 1.75;
            color: var(--ink-muted);
            max-width: 48rem;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1.3rem;
        }

        .metric-card {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem 1rem;
            background: rgba(255, 253, 247, 0.72);
        }

        .metric-value {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.9rem;
            color: var(--accent-deep);
            margin-bottom: 0.2rem;
        }

        .metric-label {
            font-size: 0.92rem;
            color: var(--ink-muted);
        }

        .chat-frame, .rail-card {
            border: 1px solid var(--line);
            background: var(--card);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            padding: 1.25rem;
            backdrop-filter: blur(8px);
        }

        .chat-frame {
            min-height: 28rem;
        }

        .chat-message {
            border-radius: 18px;
            padding: 1rem 1rem 0.95rem 1rem;
            margin-bottom: 0.85rem;
            border: 1px solid var(--line);
        }

        .chat-message.user {
            background: rgba(201, 165, 91, 0.14);
        }

        .chat-message.assistant {
            background: rgba(184, 91, 55, 0.08);
        }

        .chat-message.system {
            background: rgba(111, 117, 101, 0.08);
        }

        .chat-role {
            font-family: 'IBM Plex Mono', monospace;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.74rem;
            color: var(--olive);
            margin-bottom: 0.5rem;
        }

        .chat-content {
            color: var(--ink);
            line-height: 1.75;
            font-size: 0.99rem;
            white-space: pre-wrap;
        }

        .dossier-name {
            font-family: 'Cormorant Garamond', serif;
            font-size: 2rem;
            margin-bottom: 0.35rem;
        }

        .dossier-meta {
            color: var(--ink-muted);
            line-height: 1.7;
            font-size: 0.96rem;
        }

        .tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.8rem;
        }

        .tag-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.34rem 0.72rem;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.72);
            color: var(--ink);
            font-size: 0.83rem;
        }

        .summary-block {
            border-top: 1px solid var(--line);
            margin-top: 1rem;
            padding-top: 1rem;
            color: var(--ink-muted);
            line-height: 1.75;
        }

        .pipeline-list {
            margin-top: 0.9rem;
            display: grid;
            gap: 0.7rem;
        }

        .pipeline-row {
            border-top: 1px solid var(--line);
            padding-top: 0.7rem;
        }

        .pipeline-label {
            font-family: 'IBM Plex Mono', monospace;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.72rem;
            color: var(--olive);
            margin-bottom: 0.2rem;
        }

        .pipeline-value {
            color: var(--ink);
            line-height: 1.6;
            font-size: 0.95rem;
        }

        .starter-note {
            font-size: 0.9rem;
            color: var(--ink-muted);
            margin-bottom: 0.7rem;
        }

        .log-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--accent-deep);
        }

        .stButton > button {
            width: 100%;
            border-radius: 999px;
            border: 1px solid rgba(143, 67, 40, 0.22);
            background: linear-gradient(180deg, #c96a44 0%, #b85b37 100%);
            color: #fffdf8;
            font-weight: 600;
            padding: 0.62rem 1rem;
            box-shadow: 0 8px 20px rgba(143, 67, 40, 0.16);
        }

        .stButton > button:hover {
            border-color: rgba(143, 67, 40, 0.4);
            background: linear-gradient(180deg, #cf7350 0%, #b24e2f 100%);
            color: #fffdf8;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] input,
        .stTextInput > div > div > input {
            border-radius: 18px !important;
            border-color: var(--line) !important;
            background: rgba(255,255,255,0.75) !important;
        }

        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] input {
            font-family: 'Manrope', sans-serif !important;
        }

        .streamlit-expanderHeader {
            font-weight: 600;
        }

        @media (max-width: 900px) {
            .metric-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_shell() -> None:
    st.markdown(
        """
        <div class="salon-shell">
            <div class="log-badge">Design Layer Active</div>
            <div class="starter-note">
                Inspired by the warm editorial systems in VoltAgent's awesome-design-md collection,
                adapted into a parchment-toned historical salon for multi-turn dialogue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_setup_notice(message: str) -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="salon-kicker">Configuration Required</div>
            <div class="hero-title">The archive is ready, but the model key is missing.</div>
            <div class="hero-subtitle">
                Add your OpenAI key to <code>.env</code> or export it in the shell, then reload the page.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.error(message)


def _render_sidebar(
    persona_registry: PersonaRegistry,
    figures: list[str],
    chat_service: ChatService,
    config,
) -> str:
    st.sidebar.markdown("### Figure Selection")
    
    if st.sidebar.button("Create New Figure", type="primary"):
        _open_create_figure_dialog(config, persona_registry, chat_service)
        
    selected = st.sidebar.selectbox(
        "Choose a historical figure",
        figures,
        index=figures.index(st.session_state.selected_figure),
    )

    if selected != st.session_state.selected_figure:
        _reset_chat_state(chat_service, selected)
        st.rerun()

    dossier = persona_registry.load(selected)

    st.sidebar.markdown(
        f"""
        <div class="rail-card">
            <div class="dossier-name" style="font-size: 1.5rem;">{html.escape(dossier.name)}</div>
            <div class="dossier-meta" style="font-size: 0.85rem; margin-bottom: 0.5rem;">
                {html.escape(dossier.identity)}
            </div>
            <div class="tag-row">
                {''.join(f'<span class="tag-chip" style="font-size: 0.75rem; padding: 0.2rem 0.5rem;">{html.escape(topic)}</span>' for topic in dossier.core_topics[:3])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if persona_registry.is_custom(selected):
        with st.sidebar.expander("Manage Figure", expanded=False):
            st.caption("Custom figures can be edited as raw dossier JSON or removed entirely.")
            if st.button(
                "Edit Custom JSON",
                key=f"edit-custom::{selected}",
                use_container_width=True,
            ):
                _open_edit_custom_persona_dialog(persona_registry, chat_service, selected)

            if st.button(
                "Delete Custom Figure",
                key=f"delete-custom::{selected}",
                use_container_width=True,
            ):
                try:
                    persona_registry.delete_custom_persona(selected)
                    fallback_figure = _get_default_preset_figure(persona_registry)
                except PersonaLoaderError as exc:
                    st.error(str(exc))
                else:
                    _clear_persona_editor_state(selected)
                    _reset_chat_state(chat_service, fallback_figure)
                    st.rerun()

    if st.sidebar.button("Clear Transcript & Restart"):
        _reset_chat_state(chat_service, selected)
        st.rerun()

    return selected


def _render_hero(figure_name: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="salon-kicker">Historical Salon Interface · Active Figure: {html.escape(figure_name)}</div>
            <div class="hero-title">Converse with a historical mind, not a costume.</div>
            <div class="hero-subtitle">
                This interface is designed for long-form, grounded dialogue. It keeps the tone warm,
                editorial, and reflective while the pipeline underneath classifies, plans, generates,
                verifies, and then updates memory for {html.escape(figure_name)}.
            </div>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">5-stage</div>
                    <div class="metric-label">Classification, planning, generation, verification, and memory update remain explicit.</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Generate → Verify</div>
                    <div class="metric-label">The draft answer is checked independently before it becomes the final reply.</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Multi-turn</div>
                    <div class="metric-label">Recent context, session summary, and historical caution stay visible across dialogue.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_chat_panel(figure_name: str) -> None:
    transcript = st.session_state.transcript
    chat_html = []
    for item in transcript:
        role = item["role"]
        label = figure_name if role == "assistant" else role.capitalize()
        chat_html.append(
            (
                f'<div class="chat-message {role}">'
                f'<div class="chat-role">{html.escape(label)}</div>'
                f'<div class="chat-content">{html.escape(item["content"])}</div>'
                "</div>"
            )
        )

    empty_state = (
        '<div class="chat-message assistant">'
        f'<div class="chat-role">Welcome to {html.escape(figure_name)}\'s Salon</div>'
        "<div class=\"chat-content\">"
        f"Say hello to {html.escape(figure_name)} or ask a thoughtful question about their ideas, leadership, legacy, or modern issues through a historical lens."
        "</div>"
        "</div>"
    )
    chat_markup = "".join(chat_html) if chat_html else empty_state

    st.markdown(
        (
            '<div class="chat-frame">'
            '<div class="salon-kicker">Conversation Transcript</div>'
            f"{chat_markup}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_right_rail(dossier) -> None:
    chat_service = st.session_state.chat_service
    memory = chat_service.memory_service.get_session(st.session_state.session_id)
    latest_result = st.session_state.latest_pipeline_result

    with st.expander("Session & Perspective", expanded=True):
        st.markdown(
            f"""
            <div class="summary-block" style="border-top: none; margin-top: 0; padding-top: 0;">
                <strong>Posthumous Policy:</strong> {html.escape(dossier.posthumous_policy)}
            </div>
            <div class="summary-block">
                <strong>Session summary:</strong> {html.escape(memory.session_summary or 'No summary yet. The memory layer will compress the dialogue after enough turns accumulate.')}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Pipeline Snapshot", expanded=False):
        _render_pipeline_snapshot(latest_result, memory, dossier.name)

    with st.expander("Design Notes", expanded=False):
        st.markdown(
            """
            - Warm parchment surfaces instead of cold dashboards.
            - Serif-led editorial hierarchy for historical gravitas.
            - Terracotta accent reserved for high-signal actions.
            - Quiet cards, ring borders, and soft shadows for archive-like depth.
            """.strip()
        )


def _render_starter_prompts_at_bottom(dossier) -> str | None:
    prompts = getattr(dossier, "starter_prompts", [])
    if not prompts:
        prompts = FIGURE_PROMPTS.get(dossier.figure_id, [])
        
    if not prompts:
        return None
        
    st.markdown("<div class='starter-note' style='text-align: center; margin-top: 1rem;'>Ask your own question below, or try one of these:</div>", unsafe_allow_html=True)
    
    # We display up to 3 prompts side by side so it doesn't break UI layout as easily
    display_prompts = prompts[:3]
    cols = st.columns(len(display_prompts))
    for i, prompt in enumerate(display_prompts):
        with cols[i]:
            if st.button(prompt, key=f"bottom_starter::{dossier.figure_id}::{i}", use_container_width=True):
                return prompt
    return None


@st.dialog("Edit Custom Persona")
def _open_edit_custom_persona_dialog(
    persona_registry: PersonaRegistry,
    chat_service: ChatService,
    figure_id: str,
) -> None:
    try:
        dossier = persona_registry.load(figure_id)
    except PersonaLoaderError as exc:
        st.error(str(exc))
        return

    editor_key = _get_persona_editor_key(dossier.figure_id)
    if st.session_state.get(f"{editor_key}::loaded_for") != dossier.figure_id:
        st.session_state[editor_key] = _format_persona_json(dossier)
        st.session_state[f"{editor_key}::loaded_for"] = dossier.figure_id

    st.markdown(
        "Edit the saved `PersonaDossier` directly. The JSON is schema-validated before any changes are written."
    )
    raw_json = st.text_area(
        "PersonaDossier JSON",
        key=editor_key,
        height=420,
    )

    try:
        current_data = json.loads(raw_json)
        current_dossier = PersonaDossier.model_validate(current_data)
        warnings = PersonaLinter().lint(current_dossier)
        if warnings:
            with st.expander("⚠️ Quality Warnings", expanded=True):
                for w in warnings:
                    st.warning(f"**{w.category}**: {w.message}")
    except Exception:
        pass

    if st.button("Save Changes", type="primary"):
        try:
            parsed_data = json.loads(raw_json)
            edited_dossier = PersonaDossier.model_validate(parsed_data)
            saved_dossier = persona_registry.update_custom_persona(figure_id, edited_dossier)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno}).")
            return
        except ValidationError as exc:
            st.error(f"Schema validation failed: {exc}")
            return
        except PersonaLoaderError as exc:
            st.error(str(exc))
            return

        _clear_persona_editor_state(figure_id)
        _clear_persona_editor_state(saved_dossier.figure_id)
        st.session_state.latest_pipeline_result = None

        if saved_dossier.figure_id != figure_id:
            _reset_chat_state(chat_service, saved_dossier.figure_id)
        else:
            st.session_state.selected_figure = saved_dossier.figure_id

        st.rerun()


@st.dialog("Create a Historical Figure")
def _open_create_figure_dialog(config, persona_registry: PersonaRegistry, chat_service: ChatService) -> None:
    st.markdown("Use this form to generate a new historical figure. The system will build a unified persona dossier and conversational guidelines.")
    name = st.text_input("Figure Name (e.g., Marcus Aurelius, Rosa Parks)")
    era = st.text_input("Era / Region (optional)")
    known_for = st.text_area("Known For / Summary (optional)")
    tone_hint = st.text_input("Tone Hint (e.g., philosophical, impatient, witty)")

    if st.button("Generate Draft", type="primary"):
        if not name.strip():
            st.error("Figure Name is required.")
            return
            
        with st.spinner("Consulting the archives to build persona..."):
            builder = PersonaBuilderService(config)
            try:
                dossier = builder.build_persona(name, era, known_for, tone_hint)
                st.session_state.draft_dossier = dossier
            except Exception as e:
                st.error(f"Generation failed: {e}")

    if "draft_dossier" in st.session_state:
        dossier = st.session_state.draft_dossier
        projected_figure_id = persona_registry.reserve_custom_figure_id(dossier.figure_id or dossier.name)
        st.markdown("### Profile Preview")
        st.write(f"**Name**: {html.escape(dossier.name)}")
        st.write(f"**Figure ID**: `{projected_figure_id}`")
        st.write(f"**Identity**: {html.escape(dossier.identity)}")
        st.write(f"**Tags**: {', '.join(html.escape(t) for t in dossier.core_topics)}")
        
        prompts = getattr(dossier, "starter_prompts", [])
        if prompts:
            st.write("**Starter Prompts**:")
            for p in prompts:
                st.markdown(f"- {html.escape(p)}")

        warnings = PersonaLinter().lint(dossier)
        if warnings:
            st.markdown("---")
            st.write("**⚠️ Generation Quality Warnings**")
            for w in warnings:
                st.warning(f"**{w.category}**: {w.message}")

        if st.button("Approve and Start"):
            try:
                saved_dossier = persona_registry.save_custom_persona(
                    dossier.model_copy(update={"figure_id": projected_figure_id}),
                    overwrite=False,
                )
            except PersonaLoaderError as exc:
                st.error(str(exc))
                return

            _reset_chat_state(chat_service, saved_dossier.figure_id)
            st.session_state.pop("draft_dossier", None)
            st.rerun()


def _render_pipeline_snapshot(
    result: ChatPipelineResult | None,
    memory,
    figure_name: str,
) -> None:
    if result is None:
        st.markdown(
            f"""
            <div class="rail-card">
                <div class="salon-kicker">Pipeline Snapshot</div>
                <div class="pipeline-list">
                    <div class="pipeline-row">
                        <div class="pipeline-label">Active Figure</div>
                        <div class="pipeline-value">{html.escape(figure_name)}</div>
                    </div>
                    <div class="pipeline-row">
                        <div class="pipeline-label">Flow</div>
                        <div class="pipeline-value">
                            Question classification → response planning → response generation →
                            response verification → memory update
                        </div>
                    </div>
                    <div class="pipeline-row">
                        <div class="pipeline-label">Capture Note</div>
                        <div class="pipeline-value">
                            Ask one question to populate the latest classification and verifier result for screenshots.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    verifier_status = "not run"
    verifier_issues = "None"
    if result.verifier_result is not None:
        verifier_status = result.verifier_result.status.replace("_", " ")
        if result.verifier_result.issues:
            verifier_issues = ", ".join(
                issue.issue_type.replace("_", " ")
                for issue in result.verifier_result.issues
            )

    st.markdown(
        f"""
        <div class="rail-card">
            <div class="salon-kicker">Latest Pipeline Result</div>
            <div class="pipeline-list">
                <div class="pipeline-row">
                    <div class="pipeline-label">Question Type</div>
                    <div class="pipeline-value">{html.escape(result.classification.question_type.replace("_", " "))}</div>
                </div>
                <div class="pipeline-row">
                    <div class="pipeline-label">Answer Mode</div>
                    <div class="pipeline-value">{html.escape(result.classification.answer_mode.replace("_", " "))}</div>
                </div>
                <div class="pipeline-row">
                    <div class="pipeline-label">Verification</div>
                    <div class="pipeline-value">{html.escape(verifier_status)}</div>
                </div>
                <div class="pipeline-row">
                    <div class="pipeline-label">Verifier Issues</div>
                    <div class="pipeline-value">{html.escape(verifier_issues)}</div>
                </div>
                <div class="pipeline-row">
                    <div class="pipeline-label">Memory State</div>
                    <div class="pipeline-value">{len(memory.recent_turns)} recent turns stored in the active transcript.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _process_question(chat_service: ChatService, figure_id: str, user_question: str) -> None:
    st.session_state.transcript.append({"role": "user", "content": user_question})
    try:
        result = chat_service.chat(
            session_id=st.session_state.session_id,
            figure_id=figure_id,
            user_question=user_question,
        )
    except (PersonaLoaderError, ResponseGenerationError, ValueError, KeyError) as exc:
        st.session_state.transcript.append(
            {
                "role": "assistant",
                "content": f"I cannot answer cleanly yet because the pipeline encountered an error: {exc}",
            }
        )
        st.session_state.latest_pipeline_result = None
        return

    st.session_state.latest_pipeline_result = result
    st.session_state.transcript.append(
        {
            "role": "assistant",
            "content": result.final_answer,
        }
    )


def _get_default_preset_figure(persona_registry: PersonaRegistry) -> str:
    preset_figures = persona_registry.list_preset_figures()
    if not preset_figures:
        raise PersonaLoaderError(
            "At least one preset figure is required before deleting the active custom figure."
        )
    return preset_figures[0]


def _reset_chat_state(chat_service: ChatService, figure_id: str) -> None:
    st.session_state.selected_figure = figure_id
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.transcript = []
    st.session_state.latest_pipeline_result = None
    chat_service.start_session(
        session_id=st.session_state.session_id,
        figure_id=figure_id,
    )


def _format_persona_json(dossier: PersonaDossier) -> str:
    return json.dumps(
        dossier.model_dump(exclude_none=True),
        indent=2,
        ensure_ascii=False,
    )


def _get_persona_editor_key(figure_id: str) -> str:
    return f"custom-persona-editor::{figure_id}"


def _clear_persona_editor_state(figure_id: str) -> None:
    editor_key = _get_persona_editor_key(figure_id)
    st.session_state.pop(editor_key, None)
    st.session_state.pop(f"{editor_key}::loaded_for", None)


run_streamlit_app()
