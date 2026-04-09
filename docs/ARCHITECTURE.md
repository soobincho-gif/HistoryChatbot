# ARCHITECTURE.md

## Architecture Goal
Design a chatbot architecture that preserves:
1. character fidelity,
2. multi-turn coherence,
3. historical plausibility,
4. modular engineering quality.

---

## High-Level Architecture

```text
User Input
   ↓
Figure Selection
   ↓
Persona Dossier Load
   ↓
Session Memory Load
   ↓
Question Classification
   ↓
Response Planning
   ↓
Response Generation
   ↓
Optional Verification
   ↓
Final Answer
   ↓
Memory Update
```

---

## Layer 1: Character Layer

### Purpose

Represent the selected historical figure in a structured form.

### Input

* selected figure id

### Output

* persona dossier object

### Contents of a persona dossier

* `name`
* `era`
* `identity`
* `worldview`
* `speech_style`
* `temperament`
* `core_topics`
* `knowledge_boundary`
* `posthumous_policy`
* `taboo_or_uncertain_topics`
* `example_phrases`
* `evidence_snippets`

### Why this layer exists

Prompt-only character control is fragile.
A structured dossier keeps the figure definition explicit, reusable, and testable.

---

## Layer 2: Memory Layer

### Purpose

Preserve session continuity without blindly passing the entire transcript forever.

### Memory structure

* `recent_turns`
* `session_summary`
* `user_preferences`

### Recommended policy

* Keep only the most recent turns in full form.
* Maintain a short evolving summary of the session.
* Preserve preferences that affect answer style.

### Why this layer exists

Long raw histories become inefficient and can degrade quality.
A summary + recent-turns strategy is more stable and extensible.

---

## Layer 3: Question Analysis Layer

### Purpose

Understand what type of question the user asked before generating the final answer.

### Example question types

* factual
* philosophical/opinion
* personal-life
* posthumous/current-events
* counterfactual
* ambiguous/unclear

### Output schema example

* `question_type`
* `requires_caution`
* `is_posthumous`
* `should_refuse_direct_claim`
* `answer_mode`

### Why this layer exists

Not all questions should be answered the same way.
A classifier reduces uncontrolled generation.

---

## Layer 4: Response Planning Layer

### Purpose

Create a structured answer plan before generating natural language.

### Plan should include

* what perspective to use,
* what level of certainty is appropriate,
* whether to mention historical limits,
* what tone to adopt,
* what memory context matters,
* what facts/themes to emphasize.

### Example fields

* `stance`
* `tone_strategy`
* `historical_scope`
* `mention_uncertainty`
* `key_points`
* `avoid_claims`

### Why this layer exists

Planning improves consistency and makes behavior inspectable.

---

## Layer 5: Response Generation Layer

### Purpose

Turn the structured plan into the final in-character response.

### Inputs

* persona dossier
* recent memory
* session summary
* question classification
* response plan
* user question

### Output

* final user-facing answer

### Generation constraints

* stay in character,
* answer naturally,
* remain historically plausible,
* avoid fabricated certainty.

---

## Layer 6: Verification Layer (Optional but Recommended)

### Purpose

Check the generated answer before returning it to the user.

### Verifier checks

* is the answer in character?
* does it answer the question?
* is there obvious anachronistic certainty?
* is uncertainty expressed when needed?
* does it contradict recent session context?

### Verifier outcomes

* pass
* revise
* fail-safe fallback

### Why this layer exists

It provides a lightweight quality gate against the most common failure modes.

---

## Proposed Module Map

### `persona_loader.py`

Loads and validates persona dossier files.

### `memory_service.py`

Stores and updates recent turns and session summary.

### `question_classifier.py`

Classifies the user’s query type and risk flags.

### `response_planner.py`

Produces a structured answer plan.

### `response_generator.py`

Calls the OpenAI API and generates the final answer.

### `verifier.py`

Performs post-generation checks.

### `chat_service.py`

Coordinates the pipeline.

### `cli.py` / `ui_streamlit.py`

User interface entry points.

---

## Data Flow Example

### User message

“Einstein, what do you think of modern AI?”

### Pipeline interpretation

1. figure = Einstein
2. classify = posthumous/current-events + philosophical
3. planner = answer from Einstein-like perspective, explicitly note time-bound limitation
4. generator = in-character response with caution
5. verifier = check for character consistency and excessive certainty
6. memory update = add turn and refresh summary

---

## Error Handling Strategy

### If persona file fails to load

* return controlled application error,
* do not proceed with generation.

### If OpenAI API call fails

* return graceful fallback message,
* preserve the session if possible.

### If verifier fails

* either regenerate once or use a safe fallback response.

### If the question is too vague

* ask a short in-character clarification question.

---

## Extension Path

### V1

* fixed persona dossiers
* in-memory session memory
* CLI interface

### V2

* retrieval from evidence documents
* citations
* richer verifier
* Streamlit UI

### V3

* audio input/output
* figure library expansion
* educational mode with guided questions

---

## Architectural Principle

The chatbot should be built as a pipeline of explicit reasoning layers,
not as one giant prompt and one giant function.
