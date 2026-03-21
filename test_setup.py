from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Hello, world!"
)
print(response.text)
print(f"Tokens used: {response.usage_metadata.total_token_count}")

print("\nTest 2: Structured JSON output...")
prompt = """
Classify this support ticket:
"Production database is down!"

Return ONLY valid JSON:
{
  "category": "URGENT|NORMAL|LOW",
  "confidence": 0.0-1.0,
  "reason": "brief explanation"
}
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt
)
print(f"✓ Response: {response.text}")