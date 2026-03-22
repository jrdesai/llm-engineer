from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime


class TicketInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "I'm having trouble with the app",
                "metadata": {
                    "source": "email",
                    "user_id": "user123",
                }
            }
        }
    )

    text: str = Field(..., description="Ticket Content")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class RoutingResult(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "URGENT",
                "confidence": 0.95,
                "reason": "Ticket suggests production outage; treated as urgent.",
                "method_used": "LLM",
                "tokens_used": 123,
                "latency_ms": 123.45,
                "timestamp": "2021-01-01T00:00:00Z"
            }
        }
    )

    category: Literal["URGENT", "NORMAL", "LOW"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(..., min_length=10)
    method_used: Literal["LLM", "CLASSICAL"]
    tokens_used: int = Field(default=0, ge=0, description="Number of tokens used")
    latency_ms: float = Field(..., ge=0, description="Latency in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the routing decision")


class HealthCheck(BaseModel):
    status: Literal["healthy", "unhealthy"]
    version: str
    uptime_seconds: float
    total_requests: int
    total_tokens_used: int
    estimated_cost_usd: float
