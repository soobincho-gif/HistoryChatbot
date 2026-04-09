# SKILL.md - Memory Management

## Purpose
Preserve useful conversational continuity without blindly replaying the entire chat history.

---

## Memory components
- recent turns
- session summary
- user preferences

---

## Rules
1. Keep only recent turns in full detail.
2. Summarize older discussion into compact memory.
3. Preserve only user preferences that affect future answers.
4. Do not let stale details dominate new responses.
5. Use memory when relevant, not mechanically.

---

## Good memory behavior
If the user says:
“Earlier you said curiosity matters more than certainty. Can you connect that to education?”

The answer should recognize the earlier claim and extend it.

---

## Bad memory behavior
- forgetting a major point from two turns ago
- repeating the same introduction every answer
- referencing irrelevant old details
- stuffing the full transcript into every prompt forever

---

## Summary update strategy
After each turn:
1. store the latest user question,
2. store the latest answer,
3. update short session summary if a topic has progressed,
4. keep the summary concise and semantically useful.

---

## Repair strategy
If continuity is weak:
1. inspect recent turns passed to the model,
2. inspect summary quality,
3. reduce noise,
4. make summary more topic-centered.
