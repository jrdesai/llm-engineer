# test_reviewer.py
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from ast_analyzer import analyze_code, format_analysis_for_llm
from reviewer import CodeReviewer, ReviewResult
from main import app

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def reviewer() -> CodeReviewer:
    return CodeReviewer(model="gemini-3-flash-preview")

# ── Layer 1: AST Analyzer ─────────────────────────────────────────────────────

class TestASTAnalyzer:

    def test_detects_nested_loops(self):
        code = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
"""
        # TODO 3: analyze the code and assert loop_depth == 2 and loop_count == 2
        analysis = analyze_code(code)
        assert analysis.functions[0].loop_depth == 2
        assert analysis.functions[0].loop_count == 2

    def test_detects_recursion(self):
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        analysis = analyze_code(code)
        assert analysis.functions[0].has_recursion is True

    def test_detects_sorting(self):
        code = """
def get_top(items):
    return sorted(items)[:3]
"""
        analysis = analyze_code(code)
        assert analysis.functions[0].has_sorting is True

    def test_single_loop_no_nesting(self):
        code = """
def find_max(arr):
    max_val = arr[0]
    for x in arr:
        if x > max_val:
            max_val = x
    return max_val
"""
        analysis = analyze_code(code)
        assert analysis.functions[0].loop_depth == 1
        assert analysis.functions[0].has_recursion is False

    def test_syntax_error_returns_parse_error(self):
        analysis = analyze_code("def broken(: invalid python!!!")
        assert analysis.parse_error != ""

    def test_format_output_contains_function_name(self):
        code = """
def my_function(x):
    return x * 2
"""
        analysis = analyze_code(code)
        assert "my_function" in format_analysis_for_llm(analysis)


# ── Layer 2: CodeReviewer ─────────────────────────────────────────────────────

class TestCodeReviewer:

    def test_review_returns_review_result(self, reviewer):
        code = "def add(a, b):\n    return a + b"
        fake_analysis = "## Time: O(1)\n## Space: O(1)"

        # TODO 9: patch the chain on the reviewer instance
        # patch.object(reviewer, "chain")
        # make .invoke() return fake_analysis
        # assert result is ReviewResult and result.analysis == fake_analysis
        with patch.object(reviewer, "chain") as mock_chain:
            mock_chain.invoke.return_value = fake_analysis
            result = reviewer.review(code)
            assert isinstance(result, ReviewResult)
            assert result.analysis == fake_analysis

    def test_review_stream_yields_chunks(self, reviewer):
        code = "def add(a, b):\n    return a + b"
        fake_chunks = ["## Time", ": O(1)", "\n## Space", ": O(1)"]

        # TODO 10: patch chain's .stream() to return iter(fake_chunks)
        # collect all yielded chunks into a list
        # assert joined result equals "".join(fake_chunks)
        with patch.object(reviewer, "chain") as mock_chain:
            mock_chain.stream.return_value = iter(fake_chunks)
            chunks = list(reviewer.review_stream(code))
            assert chunks == fake_chunks


# ── Layer 3: API Endpoints ────────────────────────────────────────────────────

class TestAPI:

    def test_health_returns_ok(self, client):
        # TODO 11: GET /health, assert status 200 and body has "status": "ok"
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model": "gemini-3-flash-preview"}

    def test_health_returns_model_name(self, client):
        # TODO 12: GET /health, assert "model" key exists in response
        response = client.get("/health")
        assert response.status_code == 200
        assert "model" in response.json()

    def test_review_endpoint_returns_analysis(self, client):
        fake_result = ReviewResult(
            analysis="O(1) time",
            ast_summary="no loops",
            model_used="gemini-3-flash-preview"
        )
        # TODO 13: patch "main.reviewer.review" to return fake_result
        # POST to /review with {"code": "def add(a,b): return a+b"}
        # assert status 200 and "analysis" key in response JSON
        with patch("main.reviewer.review") as mock_review:
            mock_review.return_value = fake_result
            response = client.post("/review", json={"code": "def add(a,b): return a+b"})
            assert response.status_code == 200
            assert response.json() == fake_result.model_dump()

    def test_stream_endpoint_returns_text(self, client):
        fake_chunks = ["O(N", "^2", " time"]
        # TODO 14: patch "main.reviewer.review_stream" to return iter(fake_chunks)
        # POST to /review/stream
        # assert status 200 and response text equals "".join(fake_chunks)
        with patch("main.reviewer.review_stream") as mock_review_stream:
            mock_review_stream.return_value = iter(fake_chunks)
            response = client.post("/review/stream", json={"code": "def add(a,b): return a+b"})
            assert response.status_code == 200
            assert response.text == "".join(fake_chunks)