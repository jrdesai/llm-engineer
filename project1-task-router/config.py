"""
Configuration for Task Router
All settings in one place
"""
from typing import Dict, List

# API Configuration
API_TITLE = "Intelligent Task Router"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
Production-grade ticket routing with hybrid AI/Classical approach.

**Key Features:**
- AI classification when confidence is high
- Classical regex fallback when confidence is low
- Decision logging and cost tracking
- Evaluation metrics
"""

# Routing Configuration
CONFIDENCE_THRESHOLD = 0.75  # Use classical if LLM confidence < this
LLM_TEMPERATURE = 0.0        # Deterministic for classification
LLM_MAX_TOKENS = 512         # Limit output length (was 256; MAX_TOKENS was truncating JSON)

# Model Selection
GEMINI_MODEL = "gemini-3-flash-preview"  # Latest free model!

# Classical Router Keywords
URGENT_KEYWORDS = [
    "down", "outage", "critical", "production", 
    "cannot login", "security breach", "data loss", 
    "crash", "emergency", "urgent", "immediately", 
    "broken", "not working", "offline"
]

LOW_KEYWORDS = [
    "feature request", "enhancement", "documentation",
    "question", "how to", "tutorial", "nice to have",
    "suggestion", "idea", "could you", "would be nice"
]

# Active prompt version (key into PROMPTS)
ACTIVE_PROMPT_VERSION = "classifier_v1"

# Prompt Template (versioned for A/B testing)
PROMPTS: Dict[str, Dict] = {
    "classifier_v1": {
        "version": "1.0",
        "system": """You are an expert support ticket classifier.
        
        Categories:
        - URGENT: Production issues, security, data loss, system down
        - NORMAL: Standard bugs, non-critical issues
        - LOW: Feature requests, questions, documentation
        
        Return ONLY valid JSON.""",
        
        "template": """
        Examples:
        
        1. "Production database is down"
           → {{"category": "URGENT", "confidence": 1.0, "reasoning": "System outage affecting all users"}}
        
        2. "Feature request: Add dark mode"
           → {{"category": "LOW", "confidence": 0.9, "reasoning": "Enhancement, not blocking users"}}
        
        3. "Login page is slow but working"
           → {{"category": "NORMAL", "confidence": 0.85, "reasoning": "Performance degradation, not failure"}}
        
        Now classify:
        "{ticket_text}"
        
        Return ONLY this JSON format:
        {{
          "category": "URGENT|NORMAL|LOW",
          "confidence": 0.0-1.0,
          "reasoning": "brief explanation"
        }}
        
        JSON:
        """
    }
}

# Cost Estimation (Gemini 3 Flash pricing - check current rates)
COST_PER_1M_INPUT_TOKENS = 0.075   # Approximate
COST_PER_1M_OUTPUT_TOKENS = 0.30    # Approximate

# Evaluation Test Cases
EVALUATION_CASES = [
    {
        "text": "Production database is completely down, no one can access the system",
        "expected_category": "URGENT",
        "expected_confidence_min": 0.9
    },
    {
        "text": "Can you add a feature to export reports to PDF format?",
        "expected_category": "LOW",
        "expected_confidence_min": 0.7
    },
    {
        "text": "The dashboard is loading slowly, taking about 5 seconds",
        "expected_category": "NORMAL",
        "expected_confidence_min": 0.6
    },
    {
        "text": "Critical security vulnerability found in authentication module",
        "expected_category": "URGENT",
        "expected_confidence_min": 0.9
    },
    {
        "text": "How do I reset my password?",
        "expected_category": "LOW",
        "expected_confidence_min": 0.7
    },
    {
        "text": "Users reporting intermittent 500 errors on checkout",
        "expected_category": "URGENT",
        "expected_confidence_min": 0.8
    },
    {
        "text": "Button color doesn't match design mockup",
        "expected_category": "LOW",
        "expected_confidence_min": 0.7
    },
    {
        "text": "Some users can't upload files larger than 10MB",
        "expected_category": "NORMAL",
        "expected_confidence_min": 0.6
    },
]