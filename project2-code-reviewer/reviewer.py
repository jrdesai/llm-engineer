"""
reviewer.py — Big-O Code Reviewer using LangChain

Architecture:
    User submits code
         ↓
    AST Analyzer (tool) → structural facts extracted deterministically
         ↓
    LangChain Chain (prompt | llm | parser) → Gemini reasons about complexity
         ↓
    Streamed Big-O analysis back to user

Three new concepts vs Project 1:
    1. @tool         — wraps a Python function so the LLM can call it
    2. Chain (|)     — connects prompt → LLM → output parser in a pipeline
    3. Streaming     — yields tokens as they're generated instead of waiting for full response

WHY a chain instead of calling the LLM directly (like Project 1)?
    Chain separates concerns:
    - Prompt template is reusable and independently testable
    - LLM is swappable — change Gemini to GPT-4 in one line
    - Output parser is explicit — you declare what format you want out
    Without a chain, all three are tangled together in one blob of code.
"""

import os
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from ast_analyzer import analyze_code, format_analysis_for_llm

# Load .env from the repo root (one level up from this file)
_dir = Path(__file__).resolve().parent
load_dotenv(_dir.parent / ".env")


# ── Tool ──────────────────────────────────────────────────────────────────────
#
# @tool turns a regular Python function into a LangChain tool.
# The docstring becomes the tool's description — the LLM reads it to decide
# when and how to call the tool.
#
# WHY define it as a tool instead of just calling analyze_code() directly?
#   - Self-documenting: the docstring IS the specification
#   - The tool can be bound to the LLM via llm.bind_tools([...]) for
#     fully autonomous agents where the LLM decides when to call it
#   - We call it deterministically here, but the same tool works in
#     LangGraph agents for Project 3 without any changes

@tool
def analyze_python_code(source_code: str) -> str:
    """
    Extract structural facts from Python source code using AST parsing.
    Returns loop counts, nesting depth, recursion detection, and data structures used.
    Always call this before reasoning about time or space complexity.
    """
    analysis = analyze_code(source_code)
    return format_analysis_for_llm(analysis)


# ── Prompt Template ───────────────────────────────────────────────────────────
#
# ChatPromptTemplate defines the structure of the conversation we send to the LLM.
# {code} and {ast_analysis} are placeholders — filled in at runtime.
#
# WHY a template instead of an f-string?
#   - Templates are reusable objects — pass them around, test them independently
#   - LangChain handles message formatting (system/human roles) correctly
#   - You can version and swap prompts without touching business logic

SYSTEM_PROMPT = """You are an expert algorithms engineer and CS professor.
Your job is to analyse Python code complexity clearly and precisely.

You will receive:
1. The original Python code
2. Structural facts extracted by a deterministic AST analyser (loop counts, nesting depth, recursion, data structures)

Your response must include:
1. **Time Complexity**  — Big-O notation with a one-line justification
2. **Space Complexity** — Big-O notation with a one-line justification
3. **Why**             — Plain English explanation of what drives the complexity
4. **Optimisation**    — One concrete improvement with the resulting Big-O gain

Rules:
- Be specific — reference actual loop structure and data structures from the analysis
- Do not guess — the AST facts are ground truth, reason from them
- If the code is already optimal, say so and explain why"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """**Code submitted for review:**
```python
{code}
```

**Structural facts from AST analysis:**
{ast_analysis}

Provide your Big-O complexity analysis."""),
])


# ── Models ────────────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    """Input model — validated by Pydantic before any processing."""
    code: str
    model: str = "gemini-3-flash-preview"


class ReviewResult(BaseModel):
    """Output model for non-streaming responses."""
    analysis: str
    ast_summary: str     # The structured facts we sent to the LLM
    model_used: str


# ── Reviewer ──────────────────────────────────────────────────────────────────

class CodeReviewer:
    """
    LangChain-powered Big-O complexity reviewer.

    The chain:
        prompt | llm | StrOutputParser()

    The | pipe operator is LangChain's way of connecting components.
    Output of the left flows into the input of the right — identical
    to Unix pipes. This is called LCEL (LangChain Expression Language).

    WHY StrOutputParser at the end?
        Without it, the chain returns an AIMessage object (LangChain's internal type).
        StrOutputParser extracts just the text content — the string you actually want.
    """

    def __init__(self, model: str = "gemini-3-flash-preview"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # ChatGoogleGenerativeAI is LangChain's wrapper around the Gemini API.
        # temperature=0.1 → low randomness → consistent, factual answers.
        # For creative tasks you'd use 0.7-0.9. For factual analysis, keep it low.
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.1,
        )
        self.model = model

        # Build the chain once at init — reused for every request
        # prompt → fills in {code} and {ast_analysis} placeholders
        # llm   → sends the filled prompt to Gemini, gets AIMessage back
        # StrOutputParser → extracts the text string from AIMessage
        self.chain = prompt | self.llm | StrOutputParser()

    def review(self, code: str) -> ReviewResult:
        """
        Run analysis and return the complete result at once (non-streaming).
        Use this for API endpoints that return JSON.
        """
        # Step 1: Run the AST tool deterministically
        ast_summary = analyze_python_code.invoke(code)

        # Step 2: Run the chain — fills the prompt, calls Gemini, parses output
        analysis = self.chain.invoke({
            "code": code,
            "ast_analysis": ast_summary,
        })

        return ReviewResult(
            analysis=analysis,
            ast_summary=ast_summary,
            model_used=self.model,
        )

    def review_stream(self, code: str) -> Iterator[str]:
        """
        Run analysis and stream tokens as the LLM generates them.
        Use this for endpoints that stream responses to the client.

        WHY streaming for code review?
            Complex analysis takes 5-10 seconds. Without streaming, the user
            stares at a blank screen until the full response is ready.
            With streaming, they see words appearing immediately — the
            experience feels instant even though the total time is the same.

        Yields:
            String chunks — each chunk is one or more tokens from the LLM.
            The caller iterates over these and sends them to the client.
        """
        # AST analysis is fast and deterministic — always run it first
        ast_summary = analyze_python_code.invoke(code)

        # chain.stream() yields chunks instead of returning one complete string
        # Internally LangChain uses the Gemini streaming API
        yield from self.chain.stream({
            "code": code,
            "ast_analysis": ast_summary,
        })


# ── Quick test (run directly: python reviewer.py) ─────────────────────────────

if __name__ == "__main__":
    sample_code = """
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                duplicates.append(arr[i])
    return duplicates
"""

    reviewer = CodeReviewer(model="gemini-3-flash-preview")

    print("=" * 60)
    print("Streaming Big-O analysis...\n")
    print("=" * 60)

    for chunk in reviewer.review_stream(sample_code):
        print(chunk, end="", flush=True)

    print("\n" + "=" * 60)
