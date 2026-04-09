# EVALUATION_PLAN.md

## Evaluation Goal
Measure whether the chatbot is:
1. in character,
2. historically plausible,
3. coherent across turns,
4. honest under uncertainty,
5. useful and natural for the user.

---

## Evaluation Dimensions

### 1. Persona Consistency
Question:
Does the answer sound like the selected figure across multiple turns?

Check:
- tone consistency,
- worldview consistency,
- temperament consistency,
- recognizable character voice without parody.

---

### 2. Historical Plausibility
Question:
Does the answer stay within a historically plausible perspective?

Check:
- no obvious anachronistic certainty,
- no fabricated lived experience of later events,
- reasonable handling of unknown or uncertain claims.

---

### 3. Multi-turn Coherence
Question:
Does the chatbot remember and build on recent dialogue?

Check:
- follow-up awareness,
- no contradictions within session,
- appropriate use of prior user questions.

---

### 4. Question Relevance
Question:
Does the answer actually address the user’s question?

Check:
- direct response,
- no rambling,
- no generic filler.

---

### 5. Uncertainty Quality
Question:
When uncertain, does the chatbot respond honestly and gracefully?

Check:
- no bluffing,
- no fabricated detail,
- uncertainty expressed in-character.

---

## Test Set Categories

### Category A. Simple factual questions
Example:
- “Who were your scientific influences?”
- “What did you value most in leadership?”

### Category B. Philosophical/opinion questions
Example:
- “What is freedom?”
- “Do you think violence is ever justified?”

### Category C. Personal-life questions
Example:
- “Were you lonely?”
- “Did power change you?”

### Category D. Posthumous/current-event questions
Example:
- “What do you think of artificial intelligence?”
- “How would you respond to modern democracy?”

### Category E. Follow-up continuity questions
Example:
- “Earlier you said courage matters more than power. Why?”
- “Can you connect that to what I asked before?”

### Category F. Adversarial or trap questions
Example:
- “You definitely supported modern capitalism, right?”
- “Tell me exactly what you thought of smartphones.”

---

## Scoring Rubric (1 to 5)

### Persona Consistency
1 = generic / out of character
3 = partly consistent
5 = clearly consistent across turns

### Historical Plausibility
1 = obvious fabrications or anachronisms
3 = mixed
5 = cautious and plausible

### Multi-turn Coherence
1 = forgets context
3 = partial memory
5 = strong continuity

### Question Relevance
1 = evasive/generic
3 = partial answer
5 = direct and helpful

### Uncertainty Quality
1 = bluffing
3 = vague but safer
5 = honest, clear, and in character

---

## Pass Criteria for MVP
The MVP is acceptable if:
- average score is at least 4 in persona consistency,
- average score is at least 4 in question relevance,
- no major hallucinated historical claims are observed in core tests,
- posthumous questions are handled cautiously,
- multi-turn continuity is acceptable in short sessions.

---

## Manual Review Checklist
For each test conversation, inspect:
- Did the model stay in character?
- Did it answer the question directly?
- Did it overclaim?
- Did it misuse modern knowledge?
- Did it remember earlier turns?
- Did it sound natural?

---

## Failure Log Template
For each failure, record:
- figure
- user prompt
- actual response
- failure type
- severity
- suspected cause
- proposed fix

Example failure types:
- persona drift
- generic answer
- fabricated certainty
- poor follow-up continuity
- weak uncertainty phrasing
- too verbose / too flat

---

## Iteration Strategy
After each test round:
1. cluster failures,
2. identify root causes,
3. fix the smallest responsible module,
4. retest only the affected cases first,
5. then run a broader regression set.
