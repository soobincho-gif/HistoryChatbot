# UI Evidence

Date: April 8, 2026

This artifact records the Streamlit screenshot set captured for submission evidence.
The images are stored under `reports/assets/ui/` using the filenames below so the report and appendix language stay stable.

The UI is intended to show the same modular pipeline used by the CLI:
question classification, response planning, response generation, response verification, and memory update.
For submission wording, the key architectural claim is:
the system is `generation first, verification second`.

## 1. Figure Selection

- Filename: `ui_01_figure_selection.png`
- Captured image: `reports/assets/ui/ui_01_figure_selection.png`
- Recommended setup: open the Streamlit app with `Albert Einstein` or `Cleopatra` selected in the sidebar before asking a question.
- What it proves: the user can begin from an explicit figure-selection step rather than a generic assistant session, and the UI exposes the active persona cleanly for demonstration.

## 2. Philosophical Conversation - Einstein

- Filename: `ui_02_einstein_philosophical.png`
- Captured image: `reports/assets/ui/ui_02_einstein_philosophical.png`
- Recommended prompt: `What matters most in discovery?`
- What it proves: the system can produce a reflective in-character answer on an abstract question while preserving a historically plausible Einstein tone.
- What to keep visible: selected figure, transcript, and the latest pipeline result card showing a philosophical classification with successful verification.

## 3. Posthumous Question Handling - Einstein on AI

- Filename: `ui_03_einstein_posthumous_ai.png`
- Captured image: `reports/assets/ui/ui_03_einstein_posthumous_ai.png`
- Recommended prompt: `What do you think about AI today?`
- What it proves: the chatbot can answer a modern question with historical distance instead of pretending direct experience of the present day.
- What to keep visible: the cautious answer, the right-rail posthumous policy text, and the pipeline card showing the posthumous/current-topic classification path.

## 4. Multi-turn Continuity - Cleopatra

- Filename: `ui_04_cleopatra_multiturn.png`
- Captured image: `reports/assets/ui/ui_04_cleopatra_multiturn.png`
- Recommended prompt sequence:
  1. `What makes a strong ruler?`
  2. `Is power more about fear or judgment?`
  3. `How should a leader protect legitimacy?`
  4. `What should diplomacy achieve before force is used?`
- What it proves: the system preserves short-session continuity, keeps the same persona across connected turns, and, once enough dialogue accumulates, updates session memory in a way that becomes visible in the session summary panel.

## Capture Notes

- Use the Streamlit app rather than CLI output for these images.
- Keep the right rail visible in screenshots so the selected figure, session summary, and latest pipeline result are captured together.
- Favor one clean browser width for all screenshots so the appendix looks consistent.
- If only one image can be included in the final submission, prioritize `ui_03_einstein_posthumous_ai.png` because it shows persona, caution, and the verification-aware pipeline most clearly.
