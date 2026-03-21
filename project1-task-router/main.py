"""
FastAPI Application - Intelligent Task Router

Production-ready API with:
- Health checks
- Metrics
- Evaluation
- Error handling
- Structured JSON logging
"""
import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# setup_logging() MUST be called before importing router.py
# WHY: router.py calls logging.basicConfig() at import time.
# Our setup_logging() uses force=True to override it, but only if it runs first.
from logging_config import setup_logging
setup_logging()

from models import TicketInput, RoutingResult, HealthCheck
from router import IntelligentRouter
from config import API_TITLE, API_VERSION, API_DESCRIPTION, EVALUATION_CASES

logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# CORS (for web frontends). Use allow_credentials=False with "*" per CORS spec.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request logging middleware ---
# WHY middleware instead of logging inside each endpoint?
# Middleware runs for EVERY request automatically — you can't forget to add it.
# It also captures the full round-trip time including FastAPI's own overhead.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "http_request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
        },
    )
    return response


# Initialize router
router = IntelligentRouter()
startup_time = datetime.now()


@app.get("/", tags=["Root"])
def root():
    """API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "classify": "POST /classify",
            "metrics": "GET /metrics",
            "evaluate": "POST /evaluate"
        }
    }


@app.get("/health", response_model=HealthCheck, tags=["Monitoring"])
def health_check():
    """Health check for monitoring"""
    uptime = (datetime.now() - startup_time).total_seconds()
    metrics = router.get_metrics()
    
    return HealthCheck(
        status="healthy",
        version=API_VERSION,
        uptime_seconds=uptime,
        total_requests=metrics["total_requests"],
        total_tokens_used=metrics["total_tokens_used"],
        estimated_cost_usd=metrics["estimated_cost_usd"]
    )


@app.post("/classify", response_model=RoutingResult, tags=["Classification"])
def classify_ticket(ticket: TicketInput):
    """
    Classify a support ticket.

    Uses hybrid routing (configurable via ROUTING_MODE):
    - **classical_first** (default): Run classical rules first; call LLM only when confidence is low.
    - **llm_first**: Call LLM first; fall back to classical when confidence is low or on error.
    """
    try:
        result = router.route(ticket.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", tags=["Monitoring"])
def get_metrics():
    """Get routing metrics (LLM vs classical usage, tokens, cost)."""
    return router.get_metrics()


@app.post("/evaluate", tags=["Evaluation"])
def evaluate():
    """
    Run evaluation on test cases from config.
    Returns accuracy and per-case results.
    """
    if not EVALUATION_CASES:
        return {
            "accuracy": 0.0,
            "correct": 0,
            "total": 0,
            "results": [],
        }

    results = []
    correct = 0

    for case in EVALUATION_CASES:
        result = router.route(case["text"])

        is_correct = (
            result.category == case["expected_category"]
            and result.confidence >= case["expected_confidence_min"]
        )
        if is_correct:
            correct += 1

        results.append({
            "input": case["text"][:50] + "...",
            "expected": case["expected_category"],
            "actual": result.category,
            "confidence": result.confidence,
            "method": result.method_used,
            "correct": is_correct,
        })

    accuracy = (correct / len(EVALUATION_CASES)) * 100

    return {
        "accuracy": round(accuracy, 2),
        "correct": correct,
        "total": len(EVALUATION_CASES),
        "results": results,
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print(f"Starting {API_TITLE} v{API_VERSION}")
    print("=" * 60)
    print("\nEndpoints:")
    print("  • http://localhost:8000/")
    print("  • http://localhost:8000/docs (Swagger UI)")
    print("  • http://localhost:8000/health")
    print("  • http://localhost:8000/classify")
    print("  • http://localhost:8000/metrics")
    print("  • http://localhost:8000/evaluate")
    print("\n" + "=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)