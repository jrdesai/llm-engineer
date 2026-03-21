"""
Test Suite for Intelligent Task Router

Three layers of tests:

  Layer 1 — Unit tests (ClassicalRouter)
    Test the keyword-based router in complete isolation.
    No mocks needed — it's pure deterministic logic.

  Layer 2 — Model tests (Pydantic contracts)
    Verify that RoutingResult and TicketInput reject invalid data.
    These tests protect you from accidentally breaking your API contract.

  Layer 3 — Integration tests (IntelligentRouter)
    Test the hybrid orchestrator's decision-making logic.
    LLMRouter.route is mocked — we control exactly what the "LLM" returns
    so we can test every code path without real API calls.

WHY mock the LLM in integration tests?
    A test that calls the real API is:
    - Slow (2-3 seconds per call)
    - Costs money
    - Fails when offline or API is down
    - Non-deterministic (LLM might return slightly different results)
    You're testing YOUR routing logic, not Google's API.
    The mock lets you simulate any LLM response and test every branch reliably.
"""

import pytest
from unittest.mock import patch

from models import RoutingResult, TicketInput
from router import ClassicalRouter, IntelligentRouter


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def mock_llm_result(category="NORMAL", confidence=0.85, tokens=100):
    """
    Factory for fake LLM results used in integration tests.
    Keeps test code clean — one line instead of 7 every time.
    """
    return RoutingResult(
        category=category,
        confidence=confidence,
        reason="Mock LLM reasoning for testing purposes only",
        method_used="LLM",
        tokens_used=tokens,
        latency_ms=500.0,
    )


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def classical():
    """A fresh ClassicalRouter for each test."""
    return ClassicalRouter()


@pytest.fixture
def hybrid():
    """
    A fresh IntelligentRouter for each test.
    LLMRouter is initialized with the fake API key from conftest.py.
    Actual LLM calls are mocked per-test where needed.
    """
    return IntelligentRouter()


# ═══════════════════════════════════════════════════════════
# LAYER 1 — UNIT TESTS: ClassicalRouter
# ═══════════════════════════════════════════════════════════

class TestClassicalRouter:

    def test_urgent_two_keywords(self, classical):
        """Two urgent keywords → URGENT classification."""
        result = classical.route("production database is down")
        assert result.category == "URGENT"
        assert result.method_used == "CLASSICAL"

    def test_urgent_confidence_above_threshold(self, classical):
        """URGENT result must be confident enough to skip LLM (>= 0.75)."""
        result = classical.route("production database is down")
        assert result.confidence >= 0.75

    def test_urgent_many_keywords_caps_at_0_9(self, classical):
        """Confidence should never exceed 0.9 regardless of keyword count."""
        result = classical.route("critical production outage emergency crash down offline broken")
        assert result.confidence <= 0.9

    def test_one_urgent_keyword_not_enough(self, classical):
        """Single urgent keyword doesn't clear the threshold — falls to NORMAL."""
        result = classical.route("the system is down")  # only "down" matches
        assert result.category == "NORMAL"

    def test_low_feature_request(self, classical):
        """One low-priority keyword is enough for LOW classification."""
        result = classical.route("feature request: add dark mode to dashboard")
        assert result.category == "LOW"
        assert result.method_used == "CLASSICAL"

    def test_low_how_to_question(self, classical):
        """'how to' is a low-priority keyword."""
        result = classical.route("how to reset my password")
        assert result.category == "LOW"

    def test_low_suggestion(self, classical):
        """'suggestion' triggers LOW classification."""
        result = classical.route("suggestion: would be nice to add CSV export")
        assert result.category == "LOW"

    def test_normal_no_keywords(self, classical):
        """No keyword matches → NORMAL with default 0.6 confidence."""
        result = classical.route("the button color looks slightly off")
        assert result.category == "NORMAL"
        assert result.confidence == 0.6

    def test_case_insensitive_matching(self, classical):
        """Keywords should match regardless of case."""
        lower = classical.route("production is down")
        upper = classical.route("PRODUCTION IS DOWN")
        assert lower.category == upper.category

    def test_tokens_always_zero(self, classical):
        """Classical router never calls LLM — tokens used must always be 0."""
        result = classical.route("production is down critical outage")
        assert result.tokens_used == 0

    def test_latency_is_recorded(self, classical):
        """Latency must be a non-negative number."""
        result = classical.route("some ticket text")
        assert result.latency_ms >= 0

    def test_confidence_always_in_valid_range(self, classical):
        """Confidence must always be between 0.0 and 1.0."""
        for text in [
            "production is down critical outage crash",
            "feature request add dark mode",
            "the button looks off",
        ]:
            result = classical.route(text)
            assert 0.0 <= result.confidence <= 1.0, (
                f"Confidence {result.confidence} out of range for: {text}"
            )


# ═══════════════════════════════════════════════════════════
# LAYER 2 — MODEL TESTS: Pydantic Contracts
# ═══════════════════════════════════════════════════════════

class TestModels:

    def test_routing_result_valid(self):
        """A properly formed RoutingResult should construct without error."""
        result = RoutingResult(
            category="URGENT",
            confidence=0.95,
            reason="Production system is completely unavailable for all users",
            method_used="LLM",
            tokens_used=100,
            latency_ms=250.0,
        )
        assert result.category == "URGENT"
        assert result.confidence == 0.95
        assert result.tokens_used == 100

    def test_invalid_category_rejected(self):
        """Category must be one of URGENT, NORMAL, LOW — nothing else."""
        with pytest.raises(Exception):
            RoutingResult(
                category="MEDIUM",  # Not a valid Literal value
                confidence=0.8,
                reason="Some reason that is long enough to pass validation",
                method_used="LLM",
                tokens_used=0,
                latency_ms=10.0,
            )

    def test_confidence_above_one_rejected(self):
        """Confidence > 1.0 must be rejected by the le=1.0 constraint."""
        with pytest.raises(Exception):
            RoutingResult(
                category="URGENT",
                confidence=1.5,
                reason="Some reason that is long enough to pass validation",
                method_used="LLM",
                tokens_used=0,
                latency_ms=10.0,
            )

    def test_negative_confidence_rejected(self):
        """Confidence < 0.0 must be rejected."""
        with pytest.raises(Exception):
            RoutingResult(
                category="URGENT",
                confidence=-0.1,
                reason="Some reason that is long enough to pass validation",
                method_used="LLM",
                tokens_used=0,
                latency_ms=10.0,
            )

    def test_invalid_method_rejected(self):
        """method_used must be LLM or CLASSICAL — nothing else."""
        with pytest.raises(Exception):
            RoutingResult(
                category="URGENT",
                confidence=0.9,
                reason="Some reason that is long enough to pass validation",
                method_used="HYBRID",  # Not a valid Literal value
                tokens_used=0,
                latency_ms=10.0,
            )

    def test_ticket_input_requires_text(self):
        """TicketInput without text must fail."""
        with pytest.raises(Exception):
            TicketInput()

    def test_ticket_input_metadata_defaults_to_empty_dict(self):
        """metadata is optional and defaults to {}."""
        ticket = TicketInput(text="some ticket text")
        assert ticket.metadata == {}

    def test_ticket_input_accepts_metadata(self):
        """metadata dict should be stored as-is."""
        ticket = TicketInput(text="some ticket", metadata={"source": "email"})
        assert ticket.metadata["source"] == "email"


# ═══════════════════════════════════════════════════════════
# LAYER 3 — INTEGRATION TESTS: IntelligentRouter
# ═══════════════════════════════════════════════════════════

class TestIntelligentRouter:

    def test_classical_first_skips_llm_when_confident(self, hybrid):
        """
        The core cost-saving guarantee:
        When classical router is confident (>= 0.75), LLM must NOT be called.
        This is what achieves the ~70% cost reduction.
        """
        with patch("router.LLMRouter.route") as mock_llm:
            result = hybrid.route("production database is down critical outage")

            mock_llm.assert_not_called()  # ← The key assertion
            assert result.method_used == "CLASSICAL"
            assert result.category == "URGENT"

    def test_classical_first_calls_llm_when_uncertain(self, hybrid):
        """
        When classical is uncertain (< 0.75 confidence), LLM must be consulted.
        "button color" has no keywords → classical returns 0.6 → LLM is called.
        """
        mock_result = mock_llm_result(category="NORMAL", confidence=0.85)

        with patch("router.LLMRouter.route", return_value=mock_result):
            result = hybrid.route("the button color looks slightly off")

            assert result.method_used == "LLM"
            assert result.category == "NORMAL"

    def test_falls_back_to_classical_on_llm_error(self, hybrid):
        """
        Resilience guarantee: if LLM raises an exception (timeout, API error,
        quota exceeded), the router must still return a result — never crash.
        """
        with patch("router.LLMRouter.route", side_effect=Exception("API timeout")):
            result = hybrid.route("the button color looks slightly off")

            assert result is not None
            assert result.method_used == "CLASSICAL"  # graceful fallback
            assert result.category in ["URGENT", "NORMAL", "LOW"]

    def test_falls_back_when_llm_confidence_low(self, hybrid):
        """
        If LLM also returns low confidence (< 0.75), use the classical result.
        Neither router is sure → default to classical (cheaper, faster).
        """
        low_confidence_result = mock_llm_result(category="NORMAL", confidence=0.5)

        with patch("router.LLMRouter.route", return_value=low_confidence_result):
            result = hybrid.route("the button color looks slightly off")

            assert result.method_used == "CLASSICAL"

    def test_metrics_count_requests_correctly(self, hybrid):
        """Total request count must match number of route() calls."""
        mock_result = mock_llm_result()

        with patch("router.LLMRouter.route", return_value=mock_result):
            hybrid.route("production is down critical outage")  # classical
            hybrid.route("button color is off")                 # LLM
            hybrid.route("feature request: dark mode")          # classical (low keyword)

        metrics = hybrid.get_metrics()
        assert metrics["total_requests"] == 3

    def test_metrics_track_llm_vs_classical_split(self, hybrid):
        """Metrics must correctly attribute each routing decision."""
        mock_result = mock_llm_result(category="NORMAL", confidence=0.85)

        with patch("router.LLMRouter.route", return_value=mock_result):
            hybrid.route("production is down critical outage")  # classical (confident)
            hybrid.route("button color is off")                 # LLM (uncertain)

        metrics = hybrid.get_metrics()
        assert metrics["classical_used"] == 1
        assert metrics["llm_used"] == 1

    def test_metrics_track_llm_failures(self, hybrid):
        """LLM failures must be counted separately in metrics."""
        with patch("router.LLMRouter.route", side_effect=Exception("timeout")):
            hybrid.route("button color is off")  # LLM fails → classical fallback

        metrics = hybrid.get_metrics()
        assert metrics["llm_failed"] == 1

    def test_metrics_zero_before_any_requests(self, hybrid):
        """Fresh router with no requests must return all-zero metrics."""
        metrics = hybrid.get_metrics()
        assert metrics["total_requests"] == 0
        assert metrics["llm_used"] == 0
        assert metrics["classical_used"] == 0
        assert metrics["estimated_cost_usd"] == 0.0

    def test_result_is_always_valid_routing_result(self, hybrid):
        """
        Whatever happens, route() must return a valid RoutingResult.
        Pydantic validation means if this passes, the API response is also valid.
        """
        with patch("router.LLMRouter.route", side_effect=Exception("chaos")):
            result = hybrid.route("some random ticket text")

        assert isinstance(result, RoutingResult)
        assert result.category in ["URGENT", "NORMAL", "LOW"]
        assert 0.0 <= result.confidence <= 1.0
