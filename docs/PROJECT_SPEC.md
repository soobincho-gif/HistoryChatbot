# PROJECT_SPEC.md

## Project Title
Historical Figure Chatbot using OpenAI API

## Project Summary
This project builds a Python chatbot that allows a user to select a famous historical figure and have a multi-turn conversation with that figure.

The chatbot should:
- accept free-form user questions,
- reflect the selected figure’s tone, personality, and worldview,
- maintain conversational context across multiple turns,
- respond in a historically plausible and stylistically consistent way.

---

## Problem Statement
Most simple persona chatbots can imitate style for a short time, but they often fail in longer conversations:
- they lose character consistency,
- they become generic,
- they answer with excessive certainty,
- they blur the line between historical plausibility and fabrication.

This project aims to solve that by separating:
1. character identity,
2. conversation memory,
3. answer planning,
4. answer generation,
5. optional response verification.

---

## Primary Goal
Create a working Python chatbot that can sustain a natural, in-character, multi-turn conversation with a selected historical figure.

---

## User Inputs
The user can:
- choose a historical figure,
- ask any free-form question,
- continue asking follow-up questions in the same session.

Examples:
- “Einstein, do you think time travel is possible?”
- “Gandhi, what do you think of violence in politics?”
- “Cleopatra, how would you view modern leadership?”

---

## Expected Outputs
The chatbot should:
- answer as if the historical figure is speaking,
- maintain contextual continuity,
- reflect era, worldview, and speech style,
- remain cautious when facing uncertain or posthumous topics.

---

## Core Functional Requirements

### FR1. Figure selection
The user must be able to choose a historical figure from a predefined set.

### FR2. Free-form questioning
The user must be able to ask open-ended questions in natural language.

### FR3. Multi-turn continuity
The chatbot must preserve recent conversation context.

### FR4. Character consistency
The chatbot must stay broadly consistent with the figure’s personality and worldview.

### FR5. Historical plausibility
The chatbot must avoid obvious anachronistic certainty and fabricated facts.

### FR6. Safe uncertainty handling
When the model is uncertain, it should respond carefully rather than hallucinate.

---

## Non-Functional Requirements

### NFR1. Modularity
The system must be structured so that new figures and new modules can be added easily.

### NFR2. Readability
The codebase should be understandable by teammates.

### NFR3. Extensibility
The design should allow future upgrades such as:
- retrieval from source materials,
- citations,
- web UI,
- speech interfaces.

### NFR4. Maintainability
Core logic should be tested and documented.

---

## MVP Scope
The MVP includes:
- Python CLI or simple Streamlit interface,
- 3 sample figures,
- multi-turn chat memory,
- dossier-based persona control,
- OpenAI API integration,
- optional basic verifier.

---

## Out of Scope for MVP
Not required for first version:
- full historical citation engine,
- large-scale figure database,
- voice cloning,
- multiplayer classroom mode,
- automatic grading/assessment.

---

## Sample Historical Figures
Initial recommended set:
- Albert Einstein
- Mahatma Gandhi
- Cleopatra

Optional later additions:
- Napoleon
- Socrates
- Joan of Arc
- Marie Curie

---

## Success Criteria
A version is considered successful if:
1. the user can choose a figure,
2. the figure responds in a recognizable and consistent style,
3. the system remembers prior turns in the same session,
4. the system handles historically uncertain or posthumous questions cautiously,
5. the codebase remains modular and readable.

---

## Risks
- Persona drift in long conversations
- Generic responses
- Overconfident hallucinations
- Weak handling of posthumous/current-event questions
- Prompt logic becoming too coupled to application logic

---

## Design Principle
The product should feel like:
“a grounded conversation with a historical mind”
rather than
“a generic chatbot wearing a costume.”
