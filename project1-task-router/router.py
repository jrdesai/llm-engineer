"""
Routing Logic - Hybrid AI/Classical Approach

This module provides:
- Config‑driven prompts, thresholds, and costs (from config.py)
- NEW Google GenAI SDK pattern (client.models.generate_content)
- Structured outputs via Pydantic (no manual JSON parsing)
- Classical‑first routing by default (LLM only when needed)
- Optional LLM‑first mode via ROUTING_MODE env var
- Metrics and cost estimation helpers
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from pydantic import BaseModel

from google import genai
from google.genai import types

from models import RoutingResult
from config import (
    CONFIDENCE_THRESHOLD,
    URGENT_KEYWORDS,
    LOW_KEYWORDS,
    PROMPTS,
    ACTIVE_PROMPT_VERSION,
    GEMINI_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    COST_PER_1M_INPUT_TOKENS,
    COST_PER_1M_OUTPUT_TOKENS,
)


# ---------------------------------------------------------------------------
# Environment & client setup
# ---------------------------------------------------------------------------

# Set level to DEBUG via env to see LLM request/response details (e.g. ROUTER_DEBUG=1 or LOG_LEVEL=DEBUG)
_log_level = os.getenv("LOG_LEVEL", "").upper() or (logging.DEBUG if os.getenv("ROUTER_DEBUG") else None)
logging.basicConfig(
    level=_log_level or logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
if _log_level:
    logger.setLevel(_log_level)


def _log_empty_response(response) -> None:
    """Log why the LLM response had no usable content (for debugging empty responses)."""
    try:
        parts = []
        pf = getattr(response, "prompt_feedback", None)
        if pf is not None:
            block = getattr(pf, "block_reason", None)
            if block is not None:
                parts.append(f"prompt_feedback.block_reason={block}")
        cands = getattr(response, "candidates", None) or []
        if cands:
            c = cands[0]
            fr = getattr(c, "finish_reason", None)
            if fr is not None:
                parts.append(f"candidates[0].finish_reason={fr}")
        if parts:
            logger.info("Empty LLM response details: %s", "; ".join(parts))
    except Exception:
        pass


# Load .env from project dir and repo root so GOOGLE_API_KEY is found from any cwd
_router_dir = Path(__file__).resolve().parent
load_dotenv(_router_dir / ".env")
load_dotenv(_router_dir.parent / ".env")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Structured-output schema used by Gemini
# ---------------------------------------------------------------------------

class RouterResponseSchema(BaseModel):
    """Shape of the JSON the LLM must return."""

    category: str
    confidence: float
    reasoning: str


# ---------------------------------------------------------------------------
# Classical router (fast, cheap fallback)
# ---------------------------------------------------------------------------

class ClassicalRouter:
    """
    Classical algorithm-based router using simple keyword heuristics.
    This is the cheap, fast fallback when LLM confidence is low or unavailable.
    """

    def __init__(self) -> None:
        self.urgent_keywords = URGENT_KEYWORDS
        self.low_keywords = LOW_KEYWORDS

    def route(self, text: str) -> RoutingResult:
        start = time.perf_counter()
        text_lower = text.lower()

        urgent_count = sum(1 for kw in self.urgent_keywords if kw in text_lower)
        low_count = sum(1 for kw in self.low_keywords if kw in text_lower)

        if urgent_count >= 2:
            category = "URGENT"
            confidence = min(0.70 + urgent_count * 0.05, 0.9)
            reason = f"Matched {urgent_count} urgent keywords."
        elif low_count >= 1:
            category = "LOW"
            confidence = min(0.65 + low_count * 0.05, 0.85)
            reason = f"Matched {low_count} low-priority keywords."
        else:
            category = "NORMAL"
            confidence = 0.6
            reason = "No strong classical indicators found; defaulting to NORMAL."

        latency_ms = (time.perf_counter() - start) * 1000

        logger.info("🔧 Classical: %s (conf=%.2f)", category, confidence)

        return RoutingResult(
            category=category,
            confidence=confidence,
            reason=reason,
            method_used="CLASSICAL",
            tokens_used=0,
            latency_ms=latency_ms,
        )


# ---------------------------------------------------------------------------
# LLM router (Gemini with structured outputs)
# ---------------------------------------------------------------------------

class LLMRouter:
    """
    LLM-based router using Gemini with structured outputs.
    Uses config-driven prompts and models defined in config.py.
    """

    def __init__(self) -> None:
        self.prompt_config = PROMPTS[ACTIVE_PROMPT_VERSION]
        self.client = client
        self.model_name = GEMINI_MODEL

        logger.info("✅ Initialized LLMRouter")
        logger.info("   Model: %s", self.model_name)
        logger.info(
            "   Prompt: %s v%s",
            ACTIVE_PROMPT_VERSION,
            self.prompt_config["version"],
        )

    def route(self, text: str) -> RoutingResult:
        start = time.perf_counter()

        system_instruction = self.prompt_config["system"]
        user_prompt = self.prompt_config["template"].format(ticket_text=text)

        logger.debug("Calling LLM model=%s", self.model_name)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=LLM_TEMPERATURE,
                    max_output_tokens=LLM_MAX_TOKENS,
                    response_mime_type="application/json",
                    response_schema=RouterResponseSchema,
                ),
            )

            latency_ms = (time.perf_counter() - start) * 1000
            data = response.parsed

            # response.parsed can be None (e.g. schema mismatch, empty or blocked output)
            if data is None:
                raw = (getattr(response, "text", None) or "").strip()
                if not raw and getattr(response, "candidates", None):
                    try:
                        c = response.candidates[0]
                        if c.content and getattr(c.content, "parts", None):
                            raw = " ".join(
                                getattr(p, "text", "") or ""
                                for p in c.content.parts
                            ).strip()
                    except (IndexError, AttributeError, TypeError):
                        pass
                if not raw:
                    # Log why response is empty so you can debug (quota, safety, wrong model, etc.)
                    _log_empty_response(response)
                    logger.warning(
                        "LLM returned no content (possible safety block or empty output); classical fallback will be used"
                    )
                    raise ValueError("LLM returned empty response")
                try:
                    clean = raw.replace("```json", "").replace("```", "").strip()
                    start_idx = clean.find("{")
                    end_idx = clean.rfind("}") + 1
                    if start_idx != -1 and end_idx > start_idx:
                        clean = clean[start_idx:end_idx]
                    if not clean or not clean.strip():
                        logger.warning(
                            "LLM response contained no JSON; classical fallback will be used"
                        )
                        raise ValueError("LLM returned empty response")
                    data = RouterResponseSchema.model_validate(json.loads(clean))
                except json.JSONDecodeError as e:
                    logger.warning(
                        "LLM response was not valid JSON (%s); classical fallback will be used",
                        e,
                    )
                    raise ValueError("LLM returned empty response") from e
                except Exception as e:
                    raise ValueError(f"LLM response could not be parsed as schema: {e}") from e

            tokens_used = 0
            if getattr(response, "usage_metadata", None) is not None:
                tokens_used = response.usage_metadata.total_token_count

            logger.info(
                "🤖 Gemini: %s (conf=%.2f, tokens=%d, latency=%.0fms)",
                data.category,
                data.confidence,
                tokens_used,
                latency_ms,
            )

            return RoutingResult(
                category=data.category,
                confidence=float(data.confidence),
                reason=data.reasoning,
                method_used="LLM",
                tokens_used=tokens_used,
                latency_ms=latency_ms,
            )

        except Exception as exc:
            logger.error("❌ LLM routing failed: %s: %s", type(exc).__name__, exc)
            raise


# ---------------------------------------------------------------------------
# Intelligent hybrid router (LLM‑first with classical fallback)
# ---------------------------------------------------------------------------

class IntelligentRouter:
    """
    Hybrid router with two modes (ROUTING_MODE env):
    - classical_first (default): Classical first; call LLM only when confidence is low.
    - llm_first: LLM first; fall back to classical when confidence is low or on error.
    Tracks usage metrics and approximate cost.
    """

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD) -> None:
        self.llm_router = LLMRouter()
        self.classical_router = ClassicalRouter()
        self.confidence_threshold = confidence_threshold

        # Routing mode: "classical_first" (default) or "llm_first"
        mode = os.getenv("ROUTING_MODE", "classical_first").lower()
        if mode not in ("classical_first", "llm_first"):
            mode = "classical_first"
        self.mode = mode

        # Metrics
        self.total_requests = 0
        self.llm_used_count = 0
        self.classical_used_count = 0
        self.llm_failed_count = 0
        self.total_tokens = 0

        logger.info(
            "🚀 Initialized IntelligentRouter (threshold=%.2f, mode=%s)",
            confidence_threshold,
            self.mode,
        )

    def route(self, text: str) -> RoutingResult:
        self.total_requests += 1

        # Mode 1: classical‑first (default, cost‑aware)
        if self.mode == "classical_first":
            classical_result = self.classical_router.route(text)

            # If classical is already confident, skip LLM entirely
            if classical_result.confidence >= self.confidence_threshold:
                self.classical_used_count += 1
                logger.info(
                    "⚡ FAST PATH (classical_first): %s (conf=%.2f ≥ %.2f)",
                    classical_result.category,
                    classical_result.confidence,
                    self.confidence_threshold,
                )
                return classical_result

            # Otherwise, try LLM as a reasoning tier
            try:
                llm_result = self.llm_router.route(text)

                if llm_result.confidence >= self.confidence_threshold:
                    self.llm_used_count += 1
                    self.total_tokens += llm_result.tokens_used
                    logger.info(
                        "🤖 LLM override (classical_first): conf=%.2f ≥ %.2f",
                        llm_result.confidence,
                        self.confidence_threshold,
                    )
                    return llm_result

                # LLM also unsure → fall back to original classical decision
                self.classical_used_count += 1
                logger.info(
                    "⚠️ LLM confidence low (%.2f < %.2f), using classical result %s",
                    llm_result.confidence,
                    self.confidence_threshold,
                    classical_result.category,
                )
                return classical_result

            except Exception as exc:
                self.llm_failed_count += 1
                self.classical_used_count += 1
                logger.error("❌ LLM routing failed: %s: %s", type(exc).__name__, exc)
                logger.info("✅ Falling back to classical router due to error")
                return classical_result

        # Mode 2: LLM‑first (experimental / demo mode)
        try:
            llm_result = self.llm_router.route(text)

            if llm_result.confidence >= self.confidence_threshold:
                self.llm_used_count += 1
                self.total_tokens += llm_result.tokens_used

                logger.info(
                    "✅ Using LLM result (llm_first, conf=%.2f ≥ %.2f)",
                    llm_result.confidence,
                    self.confidence_threshold,
                )
                return llm_result

            # Low confidence → classical fallback
            self.classical_used_count += 1
            classical_result = self.classical_router.route(text)

            logger.info(
                "⚠️ LLM confidence low (%.2f < %.2f), using classical result %s",
                llm_result.confidence,
                self.confidence_threshold,
                classical_result.category,
            )
            return classical_result

        except Exception as exc:
            # LLM failure → classical fallback
            self.llm_failed_count += 1
            self.classical_used_count += 1

            logger.error("❌ LLM routing failed: %s: %s", type(exc).__name__, exc)
            logger.info("✅ Falling back to classical router due to error")

            return self.classical_router.route(text)

    def get_metrics(self) -> Dict:
        """Return aggregate routing and cost metrics."""
        if self.total_requests == 0:
            return {
                "total_requests": 0,
                "llm_used": 0,
                "llm_percentage": 0.0,
                "classical_used": 0,
                "classical_percentage": 0.0,
                "llm_failed": 0,
                "llm_failure_rate": 0.0,
                "total_tokens_used": 0,
                "estimated_cost_usd": 0.0,
                "avg_tokens_per_request": 0.0,
                "confidence_threshold": self.confidence_threshold,
                "mode": self.mode,
                "model": self.llm_router.model_name,
            }

        llm_percentage = (self.llm_used_count / self.total_requests) * 100
        classical_percentage = (self.classical_used_count / self.total_requests) * 100
        llm_failure_rate = (self.llm_failed_count / self.total_requests) * 100

        # Simple cost approximation: assume 60% input / 40% output tokens
        estimated_cost = (
            (self.total_tokens * 0.6 / 1_000_000) * COST_PER_1M_INPUT_TOKENS
            + (self.total_tokens * 0.4 / 1_000_000) * COST_PER_1M_OUTPUT_TOKENS
        )

        return {
            "total_requests": self.total_requests,
            "llm_used": self.llm_used_count,
            "llm_percentage": round(llm_percentage, 2),
            "classical_used": self.classical_used_count,
            "classical_percentage": round(classical_percentage, 2),
            "llm_failed": self.llm_failed_count,
            "llm_failure_rate": round(llm_failure_rate, 2),
            "total_tokens_used": self.total_tokens,
            "estimated_cost_usd": round(estimated_cost, 6),
            "avg_tokens_per_request": round(
                self.total_tokens / self.llm_used_count, 2
            )
            if self.llm_used_count > 0
            else 0.0,
            "confidence_threshold": self.confidence_threshold,
            "mode": self.mode,
            "model": self.llm_router.model_name,
        }


if __name__ == "__main__":
    router = IntelligentRouter()
    samples = [
        "Production database is down; customers cannot check out.",
        "How do I change my profile picture?",
        "Feature request: add dark mode to the dashboard.",
    ]

    for text in samples:
        result = router.route(text)
        print(f"\nTicket: {text[:80]}...")
        print(
            f"→ {result.category} via {result.method_used} "
            f"(conf={result.confidence:.2f}, latency={result.latency_ms:.1f}ms)"
        )

