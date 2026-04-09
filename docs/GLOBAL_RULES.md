# GLOBAL_RULES.md

## Mission
Build a Python-based historical figure chatbot that is:
1. modular,
2. readable,
3. testable,
4. grounded in historical constraints,
5. able to sustain multi-turn conversations without collapsing into generic LLM behavior.

---

## Non-Negotiable Engineering Rules

### 1. No spaghetti code
- Do not put persona loading, memory handling, prompt construction, model calls, and output formatting in one file or one function.
- Keep orchestration thin and business logic modular.
- One file should have one clear responsibility.

### 2. Strong separation of concerns
Separate the system into:
- character/persona layer,
- memory/context layer,
- response planning layer,
- response generation layer,
- optional verification layer,
- UI/CLI layer.

### 3. Prompt strings are not business logic
- Prompt templates must live in dedicated prompt files.
- Do not scatter long prompt strings across services.
- Keep prompt composition explicit and inspectable.

### 4. Persona and evidence must be separate
- Persona style, worldview, tone, and temperament belong in persona dossiers.
- Historical evidence and fact snippets belong in evidence files.
- Never mix “style instructions” and “factual evidence” into one uncontrolled blob.

### 5. Prefer structured intermediate objects
Use schemas for:
- persona dossier,
- chat turn,
- session memory,
- question classification,
- response plan,
- verifier result.

### 6. Every core service must be testable
At minimum, write lightweight tests for:
- persona loader,
- memory manager,
- question classifier,
- response planner,
- verifier.

### 7. Fail safely
If the system is uncertain:
- do not hallucinate,
- do not state fabricated historical details confidently,
- prefer historically cautious phrasing.

### 8. Make extension easy
Future upgrades should be possible without rewrites:
- add more historical figures,
- add retrieval from source materials,
- add citations,
- add Streamlit UI,
- add voice support.

---

## Coding Standards

### Python style
- Use type hints.
- Use clear function names.
- Prefer small pure functions where possible.
- Avoid deeply nested logic.
- Avoid hidden side effects.

### File design
- No god file.
- No giant class doing everything.
- Keep modules narrow and composable.

### Logging
- Log important pipeline events:
  - selected figure,
  - question type,
  - planner result,
  - generator call success/failure,
  - verifier outcome.

### Config
- Store secrets in `.env`.
- Never hardcode API keys.
- Centralize model/config settings in `config.py`.

---

## Product Behavior Rules

### Historical behavior
- The assistant must answer as if speaking from the selected figure’s perspective.
- It should reflect the figure’s era, worldview, and temperament.
- It must avoid overclaiming knowledge beyond the figure’s plausible historical horizon.

### Posthumous questions
If asked about events after the figure’s lifetime:
- do not pretend direct lived knowledge,
- answer cautiously from the figure’s perspective,
- use formulations like:
  - “From the perspective of my time...”
  - “I cannot speak from direct experience of that age, but...”

### Uncertainty
If the answer is historically uncertain:
- acknowledge uncertainty,
- avoid fabricated precision,
- stay in character while remaining honest.

### Multi-turn continuity
- The system must preserve local conversational continuity.
- It should remember recent user questions and its own prior answers.
- It should avoid contradicting itself within the same session.

---

## Development Workflow Rules

### Iterative loop
For each development step:
1. implement one focused unit,
2. test it,
3. inspect failure modes,
4. refine,
5. only then move forward.

### Recommended implementation order
1. schemas
2. persona loader
3. memory manager
4. question classifier
5. planner
6. generator
7. verifier
8. CLI/UI

### Never do this
- Do not build the full app in one pass.
- Do not skip docs.
- Do not skip tests for core logic.
- Do not optimize UI before pipeline quality is acceptable.
