"""
pytest configuration — runs before any test file is loaded.

WHY this file exists:
    When pytest imports router.py, Python executes the module-level code including:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key: raise ValueError(...)

    This would crash every test run unless GOOGLE_API_KEY is set.
    We don't want tests to depend on a real API key — that couples your test
    suite to an external service. Instead, we inject a fake key here so the
    import succeeds, then mock the actual API calls inside each test.
"""
import os

# Set a fake key before any test imports router.py
# The real API is never called — LLMRouter.route is mocked in tests that need it
os.environ.setdefault("GOOGLE_API_KEY", "test-fake-key-not-real")
