"""Score API endpoints."""

import re

from fastapi import APIRouter, HTTPException, Path, Query

from ..dependencies import get_score_calculator
from ..schemas.score import (
    ErrorResponse,
    ScoreHistoryItem,
    ScoreHistoryResponse,
    ScoreResponse,
)

router = APIRouter(prefix="/score", tags=["score"])


def validate_address(address: str) -> str:
    """Validate Ethereum address format."""
    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_address", "message": f"Invalid Ethereum address: {address}"},
        )
    return address.lower()


@router.get(
    "/{agent_address}",
    response_model=ScoreResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid address"},
        404: {"model": ErrorResponse, "description": "Agent not registered"},
    },
    summary="Get agent score",
    description="Get the AgentFICO score for an agent.",
)
async def get_score(
    agent_address: str = Path(..., description="Agent Ethereum address"),
    days: int = Query(30, ge=1, le=365, description="Analysis period (days)"),
) -> ScoreResponse:
    """Get the AgentFICO score for an agent.

    - **agent_address**: Agent Ethereum address (0x...)
    - **days**: Analysis period (default 30 days, max 365 days)

    Returns:
        - overall: Overall score (0-1000)
        - txSuccess: Transaction success rate score (0-100)
        - x402Profitability: x402 profitability score (0-100)
        - erc8004Stability: ERC-8004 stability score (0-100)
        - riskLevel: Risk level (1-5)
        - confidence: Confidence score (0-100)
    """
    address = validate_address(agent_address)

    calculator = get_score_calculator()

    try:
        result = await calculator.calculate_score(address, days)
        return ScoreResponse(
            agent_address=result.agent_address,
            overall=result.overall,
            tx_success=result.tx_success,
            x402_profitability=result.x402_profitability,
            erc8004_stability=result.erc8004_stability,
            risk_level=result.risk_level.value,
            risk_level_name=result.risk_level.name.lower(),
            confidence=result.confidence,
            timestamp=result.timestamp,
            breakdown=result.breakdown,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "calculation_error", "message": str(e)},
        )


@router.get(
    "/{agent_address}/history",
    response_model=ScoreHistoryResponse,
    summary="Get score history",
    description="Get the score history for an agent.",
)
async def get_score_history(
    agent_address: str = Path(..., description="Agent Ethereum address"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve"),
) -> ScoreHistoryResponse:
    """Get the score history for an agent.

    Currently returns mock data.
    In production, this will query the database for historical records.
    """
    address = validate_address(agent_address)

    # TODO: Implement actual DB query
    # Currently returns only the current score
    calculator = get_score_calculator()
    result = await calculator.calculate_score(address)

    return ScoreHistoryResponse(
        agent_address=address,
        history=[
            ScoreHistoryItem(
                overall=result.overall,
                risk_level=result.risk_level.value,
                timestamp=result.timestamp,
            )
        ],
        total_count=1,
    )


@router.post(
    "/{agent_address}/refresh",
    response_model=ScoreResponse,
    summary="Refresh score",
    description="Force recalculate the agent's score.",
)
async def refresh_score(
    agent_address: str = Path(..., description="Agent Ethereum address"),
    days: int = Query(30, ge=1, le=365, description="Analysis period (days)"),
) -> ScoreResponse:
    """Force recalculate the agent's score.

    Bypasses the cache and recalculates with fresh data.
    """
    address = validate_address(agent_address)

    calculator = get_score_calculator()

    # TODO: Add cache invalidation logic
    result = await calculator.calculate_score(address, days)
    return ScoreResponse(
        agent_address=result.agent_address,
        overall=result.overall,
        tx_success=result.tx_success,
        x402_profitability=result.x402_profitability,
        erc8004_stability=result.erc8004_stability,
        risk_level=result.risk_level.value,
        risk_level_name=result.risk_level.name.lower(),
        confidence=result.confidence,
        timestamp=result.timestamp,
        breakdown=result.breakdown,
    )
