# Intelligent Task Router

A FastAPI service that classifies support tickets into **URGENT**, **NORMAL**, or **LOW** using a hybrid approach: keyword-based rules first, with an optional LLM (Gemini) step when the result is ambiguous.

## Features

- **Hybrid routing**: Classical keyword rules for obvious cases; LLM only when needed (configurable).
- **Two modes** (env `ROUTING_MODE`):
  - **classical_first** (default): Run classical rules first; call the LLM only when confidence is below threshold. Saves cost and latency.
  - **llm_first**: Call the LLM first; fall back to classical on low confidence or error.
- **Structured outputs**: Gemini returns JSON validated with Pydantic; no brittle string parsing.
- **Metrics & cost**: Tracks LLM vs classical usage, token count, and estimated cost.
- **Evaluation**: Built-in test cases and `POST /evaluate` for accuracy checks.
- **Graceful fallback**: If the LLM fails or returns empty/blocked, the classical router is used.

## Setup

### Prerequisites

- Python 3.12+ (3.12 recommended for dependency compatibility)
- A [Google AI Studio](https://aistudio.google.com/apikey) API key (Gemini)

### Installation

From the repo root (or from this directory if using a local venv):

```bash
cd /path/to/llm-engineer
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r project1-task-router/requirements.txt
```

### Environment

Create a `.env` file in the repo root or in `project1-task-router/`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Optional:

- `ROUTING_MODE=classical_first` or `llm_first` (default: `classical_first`)
- `ROUTER_DEBUG=1` or `LOG_LEVEL=DEBUG` — enable debug logs to confirm LLM calls and inspect empty responses

## Run

From the repo root with venv activated:

```bash
python project1-task-router/main.py
```

Or with uvicorn:

```bash
uvicorn project1-task-router.main:app --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Swagger UI: http://localhost:8000/docs  

## API Endpoints

| Method | Path        | Description |
|--------|-------------|-------------|
| GET    | `/`         | Service name, version, and list of endpoints |
| GET    | `/health`   | Health check: status, uptime, total requests, tokens, estimated cost |
| POST   | `/classify` | Classify a ticket. Body: `{"text": "your ticket text", "metadata": {}}` |
| GET    | `/metrics`  | Routing metrics: LLM vs classical usage, tokens, cost, mode |
| POST   | `/evaluate` | Run evaluation on test cases from config; returns accuracy and per-case results |

### Example: Classify a ticket

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Production database is down; customers cannot checkout."}'
```

Response includes `category`, `confidence`, `reason`, `method_used` (LLM or CLASSICAL), `tokens_used`, and `latency_ms`.

## Project structure

```
project1-task-router/
├── main.py          # FastAPI app and routes
├── router.py        # ClassicalRouter, LLMRouter, IntelligentRouter
├── config.py        # Thresholds, keywords, prompts, model, evaluation cases
├── models.py        # Pydantic: TicketInput, RoutingResult, HealthCheck
├── requirements.txt
├── README.md
└── test_router.py   # Tests (pytest)
```

Configuration (model, threshold, keywords, prompts, cost constants) lives in `config.py`. The router loads `.env` from this directory and from the repo root so the API key is found regardless of working directory.

## Configuration (config.py)

- **CONFIDENCE_THRESHOLD** — Use LLM only when classical confidence is below this (e.g. 0.75).
- **GEMINI_MODEL** — Model name (e.g. `gemini-3-flash-preview` or `gemini-2.0-flash`).
- **LLM_MAX_TOKENS** — Max output tokens (increase if you see `FinishReason.MAX_TOKENS` and empty JSON).
- **URGENT_KEYWORDS** / **LOW_KEYWORDS** — Keyword lists for the classical router.
- **PROMPTS** / **ACTIVE_PROMPT_VERSION** — Versioned prompt templates for the LLM.
- **EVALUATION_CASES** — Test cases used by `POST /evaluate`.

## Troubleshooting

- **"GOOGLE_API_KEY not found"** — Add `GOOGLE_API_KEY` to `.env` in the repo root or in `project1-task-router/`.
- **"LLM returned empty response"** — Check logs for `Empty LLM response details: ...`. Common causes:
  - **MAX_TOKENS**: Increase `LLM_MAX_TOKENS` in `config.py` (e.g. 512).
  - **Quota**: Check [ai.dev/rate-limit](https://ai.dev/rate-limit) and billing.
  - **Model**: Ensure `GEMINI_MODEL` is available for your key (e.g. try `gemini-2.0-flash`).
- **Debug LLM calls** — Run with `ROUTER_DEBUG=1` or `LOG_LEVEL=DEBUG` to see when the LLM is called and why a response might be empty.

## License

Use as needed for learning or personal projects.
