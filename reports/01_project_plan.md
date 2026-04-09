# Project Plan

Date: April 8, 2026

## Product Goal

Build a historically grounded, multi-turn chatbot that speaks from the perspective of selected historical figures while preserving persona consistency, memory, and posthumous caution.

## Architecture Plan

1. Create typed schemas for persona, memory, classification, planning, and verification.
2. Load persona dossiers from structured JSON files.
3. Maintain in-memory session state with recent turns and summary memory.
4. Classify incoming questions before generation.
5. Translate classification into a structured response plan.
6. Generate final prose with the OpenAI Responses API.
7. Add verification and regeneration layers.
8. Deliver both CLI and Streamlit interfaces.

## Design Plan

1. Review VoltAgent's `awesome-design-md` collection.
2. Select a design direction that fits a history-focused conversational product.
3. Create a project-root `DESIGN.md`.
4. Apply that system to the Streamlit UI.
5. Keep the UI aligned with the product promise: grounded conversation, not generic chatbot chrome.

## Reporting Plan

Collect the following in one folder:
- project plan,
- completed milestones,
- change log,
- design rationale,
- validation notes,
- next-step backlog.
