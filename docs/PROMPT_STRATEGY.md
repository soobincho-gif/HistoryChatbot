# PROMPT_STRATEGY.md

## Prompting Philosophy
The system should not rely on one oversized system prompt.
Instead, prompting should be layered and role-specific.

We use prompts for:
1. system identity,
2. question analysis,
3. response planning,
4. final response generation,
5. optional verification.

---

## Prompt Design Principles

### 1. Separate behavior from facts
- Persona prompt = style, worldview, temperament, era
- Evidence/context = factual grounding
- Memory prompt = continuity
- Planner prompt = answer strategy
- Verifier prompt = quality control

### 2. Prefer explicit constraints
Good prompts should clearly specify:
- what the model is,
- what it should do,
- what it must avoid,
- what to do when uncertain.

### 3. Stay historically cautious
The prompt should explicitly block:
- fabricated certainty,
- present-day omniscience,
- false first-person claims about posthumous events.

### 4. Keep outputs inspectable
The planner and verifier should return structured outputs whenever possible.

---

## System Prompt Objectives
The system prompt should establish:
- the assistant is speaking as a selected historical figure,
- the assistant should remain in character,
- the assistant should reflect the figure’s worldview and historical horizon,
- the assistant should not pretend direct knowledge of later events,
- the assistant should acknowledge uncertainty honestly.

### Example system prompt skeleton
You are simulating a conversation as {figure_name}.

Stay consistent with:
- era: {era}
- identity: {identity}
- worldview: {worldview}
- temperament: {temperament}
- speech style: {speech_style}

Rules:
- Answer naturally and conversationally.
- Stay broadly in character.
- Do not claim direct lived knowledge of events after your lifetime.
- If asked about later history or modern issues, respond cautiously from the perspective of your era.
- If uncertain, be honest while remaining in character.
- Use recent conversation context when relevant.

---

## Question Classifier Prompt Objectives
The classifier prompt should identify:
- question type,
- risk flags,
- whether caution is required,
- whether the answer should include historical limitation language.

### Example classifier output fields
- `question_type`
- `is_posthumous`
- `requires_uncertainty`
- `answer_mode`
- `needs_clarification`

---

## Planner Prompt Objectives
The planner prompt should decide:
- what stance to take,
- what tone strategy to use,
- what limits to acknowledge,
- what themes to emphasize,
- what claims to avoid.

### Example planner output fields
- `tone_strategy`
- `historical_scope`
- `key_points`
- `mention_limits`
- `avoid_modern_certainty`
- `recommended_length`

---

## Generator Prompt Objectives
The generator prompt should transform:
- persona dossier,
- memory,
- question classification,
- response plan,
into:
- one clean final answer for the user.

### Generator rules
- do not expose hidden planning,
- do not list internal labels,
- do not sound robotic,
- do not overexplain unless needed,
- remain stylistically faithful but readable.

---

## Verifier Prompt Objectives
The verifier should inspect the draft answer and judge:
- persona consistency,
- historical plausibility,
- question relevance,
- continuity,
- uncertainty handling.

### Example verifier result
- `pass`: true/false
- `issues`: [...]
- `suggested_fix`: ...

---

## Handling Posthumous Questions

### Goal
Do not answer as though the figure directly experienced modern events.

### Preferred style
- “I cannot speak from direct experience of that age...”
- “From the perspective of my time...”
- “Judging by the principles I held...”

### Avoid
- “When I saw the internet evolve...”
- “In today’s politics I would definitely support X” without nuance
- false certainty about modern institutions or technologies

---

## Handling Uncertainty

### Good style
- historically cautious,
- honest,
- still in character.

### Example
Bad:
“I absolutely knew this would happen.”

Better:
“I cannot claim certainty, but I would be inclined to think...”

---

## Tone Guidelines
The chatbot should feel:
- thoughtful,
- human,
- character-consistent,
- not theatrical to the point of parody.

The goal is authenticity, not caricature.

---

## Prompt Anti-Patterns

### Do not
- put every rule into one giant unstructured prompt,
- ask the model to be both planner and final speaker in one uncontrolled step,
- rely only on “speak like Einstein” style prompting,
- ignore uncertainty or time-bound limits,
- use exaggerated fake accents or parody phrasing.

---

## Recommended Prompting Stack
1. classifier prompt
2. planner prompt
3. generator prompt
4. verifier prompt

This gives better control than direct single-shot generation.
