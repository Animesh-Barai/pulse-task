# AI Service Core

## Purpose
The AI Service is a dedicated microservice that executes machine learning inference (local DistilBERT) and manages cloud LLM orchestration (Google Gemini). It is decoupled from the main backend to allow independent scaling of compute-intensive AI workloads.

## Public API
### REST Endpoints (Internal Only)
- `POST /ai/suggest/task`: Performs task classification and rewrite generation.
- `POST /ai/prioritize`: Runs the prioritization algorithm on a batch of tasks.
- `GET /health`: Returns service health and model status.

## Data Models
### TaskSuggestionRequest
- `raw_title`: String.
- `raw_description`: Optional string.
- `context`: JSON object.

### TaskSuggestionResponse
- `rewritten_title`: Optimized title.
- `checklist`: 3-5 sub-tasks.
- `suggested_priority`: 1-5 scale.
- `confidence`: 0.0-1.0.
- `explanation`: Reason for the prediction.

## Events Emitted/Consumed
- **Emitted**: None (Service is primarily a stateless inference engine).
- **Consumed**: None.

## Invariants
- Output must strictly follow the JSON schema for integration reliability.
- Latency for local model must be < 100ms.
- LLM fallback must strictly adhere to the prompt guardrails (Appendix B of PRD).

## Edge Cases
- **API Key Missing**: Falls back to a "scaffold" mode returning baseline suggestions with lower confidence.
- **Model Loading Error**: Service returns 500 with graceful failure in the main application (falling back to heuristics).
- **Network Timeout**: Backend handles AI service timeouts via Celery retries.

## Test Coverage
- Unit tests for prompt engineering in `ai-service/tests/test_prompts.py`.
- Functional tests for the FastAPI service in `ai-service/tests/test_main.py`.
