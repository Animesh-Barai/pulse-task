# AI Orchestration Module

## Purpose
The AI Orchestration module in the backend acts as a bridge between the business logic (Tasks) and the AI Core service. It handles input validation, caching, rate limiting, and asynchronous job submission for task improvements.

## Public API
### REST Endpoints
- `POST /ai/suggest/task`: Triggers a task rewrite suggestion.
- `POST /ai/prioritize`: Calculates effective priority for a list of tasks.
- `POST /ai/train/feedback`: Receives user feedback for continuous learning.

### Background Jobs (Celery)
- `process_ai_task`: Asynchronously calls the AI Core service and updates the task metadata.
- `process_llm_fallback`: Invoked when the local model confidence is low.

## Data Models
### AISuggestionRequest
- `raw_title`: Task title to optimize.
- `raw_description`: Task description to optimize.
- `context`: Workspace and user context for personalization.

### AISuggestionResponse
- `rewritten_title`: AI-generated improvement.
- `checklist`: Actionable sub-tasks.
- `suggested_priority`: 1-5 rating.
- `suggested_due_date`: Calendar-aware suggestion.
- `confidence`: Numeric score 0-1.
- `explanation`: Reason for the suggestion.

## Events Emitted/Consumed
- **Emitted**: `task_updated` (via TaskService after AI results are applied), `ai:suggestion` (socket event).
- **Consumed**: `task_created` (triggers automatic suggestion job).

## Invariants
- AI suggestions must conform to a strict JSON schema.
- Suggestions are cached in Redis for 24 hours to reduce LLM costs.
- Confidence < 0.5 must be flagged for human review.

## Edge Cases
- **Low Confidence**: Triggers fallback to LLM (Gemini) instead of local classifier.
- **Service Down**: Heuristic-based fallback ensures the system remains functional even if the AI service is offline.
- **Rate Limiting**: Applied per workspace to prevent API abuse.

## Test Coverage
- Unit tests for suggestion logic in `backend/tests/unit/test_classifier_service.py`.
- Integration tests for AI job flows in `backend/tests/integration/test_ai_api.py`.
- Heuristic fallback validation in `backend/tests/unit/test_heuristics_service.py`.
