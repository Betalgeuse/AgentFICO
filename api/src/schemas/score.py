"""Score response schemas for API endpoints."""

from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class RiskLevelEnum(IntEnum):
    """Risk level classification (1: lowest risk ~ 5: highest risk)."""

    EXCELLENT = 1
    GOOD = 2
    AVERAGE = 3
    BELOW_AVERAGE = 4
    POOR = 5


class ScoreResponse(BaseModel):
    """Score query response."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    agent_address: str
    overall: int = Field(..., ge=0, le=1000, description="Overall score (0-1000)")
    tx_success: int = Field(
        ..., ge=0, le=100, description="Transaction success rate score"
    )
    x402_profitability: int = Field(
        ..., ge=0, le=100, description="x402 profitability score"
    )
    erc8004_stability: int = Field(
        ..., ge=0, le=100, description="ERC-8004 stability score"
    )
    risk_level: int = Field(
        ..., ge=1, le=5, description="Risk level (1=lowest, 5=highest)"
    )
    risk_level_name: str = Field(..., description="Risk level name")
    confidence: int = Field(..., ge=0, le=100, description="Confidence score")
    timestamp: datetime
    breakdown: Optional[Dict[str, Any]] = None


class ScoreHistoryItem(BaseModel):
    """Score history item."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    overall: int
    risk_level: int
    timestamp: datetime


class ScoreHistoryResponse(BaseModel):
    """Score history response."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    agent_address: str
    history: list[ScoreHistoryItem]
    total_count: int


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
