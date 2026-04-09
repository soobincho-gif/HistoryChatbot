# Change Log

Date: April 8, 2026

## Major Changes

### Data and Schemas
- Replaced the early scaffold schema with the current persona/memory/classification/plan/verifier contract.
- Added persona JSON fixtures and validation tests.

### Services
- Implemented `PersonaLoader`.
- Implemented `MemoryService`.
- Implemented `QuestionClassifier`.
- Implemented `ResponsePlanner`.
- Implemented `ChatService`.
- Implemented `OpenAIResponseGenerator`.
- Formalized `app/services/verifier.py` as the shared verifier contract layer.
- Implemented `SimpleVerifier`.

### Prompts
- Replaced the placeholder prompt template with explicit instruction and input builders.

### Interfaces
- Replaced the placeholder CLI with a real multi-turn CLI.
- Replaced the placeholder Streamlit file with a designed conversational UI.
- Connected verifier checks to the runtime chat paths.

### Project Operations
- Added `.env` autoload support.
- Added `.gitignore`.
- Added report-log documents for later writeups.
- Added curated transcript appendices for report-ready qualitative evidence.

## Files Most Recently Added or Updated

- `README.md`
- `app/services/verifier.py`
- `app/services/simple_verifier.py`
- `app/services/chat_service.py`
- `tests/test_verifier.py`
- `reports/08_transcript_philosophical_einstein.md`
- `reports/09_transcript_posthumous_ai.md`
- `reports/10_transcript_multiturn_cleopatra.md`
