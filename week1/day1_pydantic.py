from pydantic import BaseModel, Field
from typing import Literal
from google import genai
from google.genai import errors as genai_errors
import os
import json
import time

from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# Prefer flash; fall back to another model on 503; retry on 429 (quota)
MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]
MAX_RETRIES = 3
RETRY_DELAY_SEC = 2
QUOTA_RETRY_DELAY_SEC = 60  # 429 says "retry in ~58s"

class TicketClassification(BaseModel):
    category: Literal["URGENT", "NORMAL", "LOW"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=10)

def classify_ticket(ticket: str) -> TicketClassification:
    # Demo mode: return mock result without calling API (e.g. when quota exhausted)
    if os.environ.get("USE_DEMO_RESPONSE", "").lower() in ("1", "true", "yes"):
        return TicketClassification(
            category="URGENT",
            confidence=0.95,
            reason="Demo response: ticket suggests production outage; treated as urgent.",
        )

    schema = TicketClassification.model_json_schema()
    prompt = f"""   
    Classify this support ticket:
    {ticket}

    Return ONLY valid JSON matching the following schema:
    {json.dumps(schema, indent=2)}

    JSON: 
    """

    last_error = None
    for model in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                return TicketClassification.model_validate_json(clean_json)
            except genai_errors.ServerError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SEC)
                continue
            except genai_errors.ClientError as e:
                last_error = e
                # 429 = quota exceeded; wait and retry
                if e.code == 429 and attempt < MAX_RETRIES - 1:
                    time.sleep(QUOTA_RETRY_DELAY_SEC)
                    continue
                raise
        # Try next model
        time.sleep(RETRY_DELAY_SEC)

    raise last_error or RuntimeError("No model succeeded")


if __name__ == "__main__":
    if os.environ.get("USE_DEMO_RESPONSE", "").lower() in ("1", "true", "yes"):
        print("(Demo mode: using mock response; set USE_DEMO_RESPONSE=0 to call the API)\n")

    ticket = "Production database is down!"
    result = classify_ticket(ticket)
    print(f"Classification: {result}")
    print(f"Reason: {result.reason}")
    print(f"Confidence: {result.confidence}")
    print(f"Category: {result.category}")

    # Test case 2: Low priority
    print("\n2. Testing low priority ticket...")
    result2 = classify_ticket("Can you add dark mode to the app?")
    print(f"   Category: {result2.category}")
    print(f"   Confidence: {result2.confidence}")
    print(f"   Reasoning: {result2.reason}")
    
    # Test case 3: Normal
    print("\n3. Testing normal ticket...")
    result3 = classify_ticket("The dashboard loads slowly")
    print(f"   Category: {result3.category}")
    print(f"   Confidence: {result3.confidence}")
    print(f"   Reasoning: {result3.reason}")
    
    print("\n" + "=" * 60)
    print("✓ Pydantic validation works!")
    print("✓ Type safety ensured")
    print("✓ Ready to build Project 1")
    print("=" * 60)