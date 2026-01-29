"""Contract API endpoints for direct blockchain interaction."""

import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.contract_client import ContractClient


router = APIRouter(prefix="/contract", tags=["contract"])


def get_contract_client() -> ContractClient:
    """환경 변수에서 컨트랙트 클라이언트 생성"""
    rpc_url = os.getenv("RPC_URL", "http://127.0.0.1:8545")
    contract_address = os.getenv(
        "CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    )
    private_key = os.getenv("OWNER_PRIVATE_KEY")

    return ContractClient(rpc_url, contract_address, private_key)


class UpdateScoreRequest(BaseModel):
    """Request body for updating an agent's score."""

    tx_success: int = Field(..., ge=0, le=100, description="Transaction success score (0-100)")
    x402_profitability: int = Field(..., ge=0, le=100, description="X402 profitability score (0-100)")
    erc8004_stability: int = Field(..., ge=0, le=100, description="ERC8004 stability score (0-100)")
    confidence: int = Field(..., ge=0, le=100, description="Confidence level (0-100)")
    risk_level: str = Field(..., pattern="^(low|medium|high)$", description="Risk level")
    ipfs_breakdown: Optional[str] = Field("", description="IPFS hash for detailed breakdown")


class ScoreResponse(BaseModel):
    """Response for score queries."""

    overall: int
    txSuccess: int
    x402Profitability: int
    erc8004Stability: int
    confidence: int
    riskLevel: str
    timestamp: int
    ipfsBreakdown: str


class UpdateScoreResponse(BaseModel):
    """Response for score update."""

    tx_hash: str
    status: str


class RiskAssessmentResponse(BaseModel):
    """Response for risk assessment."""

    riskLevel: int
    defaultProbability: int
    expectedLoss: int
    positiveFactors: list[str]
    riskFactors: list[str]


class ContractStatsResponse(BaseModel):
    """Response for contract statistics."""

    total_agents: int
    contract_address: str
    is_connected: bool


@router.get("/score/{agent_address}", response_model=ScoreResponse)
async def get_contract_score(agent_address: str):
    """컨트랙트에서 점수 조회

    - **agent_address**: Agent Ethereum address (0x...)

    Returns the full score data from the blockchain contract.
    """
    client = get_contract_client()

    if not client.is_connected():
        raise HTTPException(status_code=503, detail="RPC connection unavailable")

    try:
        score = await client.get_score(agent_address)
        return ScoreResponse(**score)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract call failed: {str(e)}")


@router.post("/score/{agent_address}", response_model=UpdateScoreResponse)
async def update_contract_score(
    agent_address: str,
    request: UpdateScoreRequest,
):
    """컨트랙트에 점수 업데이트 (owner only)

    - **agent_address**: Agent Ethereum address (0x...)

    Updates the agent's score on the blockchain.
    Requires OWNER_PRIVATE_KEY environment variable to be set.
    """
    client = get_contract_client()

    if not client.is_connected():
        raise HTTPException(status_code=503, detail="RPC connection unavailable")

    try:
        tx_hash = await client.update_score(
            agent_address,
            request.tx_success,
            request.x402_profitability,
            request.erc8004_stability,
            request.confidence,
            request.risk_level,
            request.ipfs_breakdown or "",
        )
        return UpdateScoreResponse(tx_hash=tx_hash, status="success")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")


@router.get("/risk/{agent_address}", response_model=RiskAssessmentResponse)
async def assess_contract_risk(
    agent_address: str,
    amount_usdc: int = Query(..., ge=0, description="Amount in USDC units"),
    protocol_type: str = Query(
        ..., pattern="^(lending|trading|payment)$", description="Protocol type"
    ),
):
    """컨트랙트에서 리스크 평가

    - **agent_address**: Agent Ethereum address (0x...)
    - **amount_usdc**: Amount in USDC units to assess
    - **protocol_type**: Type of protocol (lending, trading, or payment)

    Returns risk assessment from the blockchain contract.
    """
    client = get_contract_client()

    if not client.is_connected():
        raise HTTPException(status_code=503, detail="RPC connection unavailable")

    try:
        risk = await client.assess_risk(agent_address, amount_usdc, protocol_type)
        return RiskAssessmentResponse(**risk)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract call failed: {str(e)}")


@router.get("/registered/{agent_address}")
async def check_registered(agent_address: str):
    """에이전트 등록 여부 확인

    - **agent_address**: Agent Ethereum address (0x...)

    Returns whether the agent is registered in the contract.
    """
    client = get_contract_client()

    if not client.is_connected():
        raise HTTPException(status_code=503, detail="RPC connection unavailable")

    try:
        is_registered = await client.is_registered(agent_address)
        return {"agent_address": agent_address, "is_registered": is_registered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract call failed: {str(e)}")


@router.get("/stats", response_model=ContractStatsResponse)
async def get_contract_stats():
    """컨트랙트 통계

    Returns contract statistics including total agents and connection status.
    """
    client = get_contract_client()

    is_connected = client.is_connected()

    if not is_connected:
        return ContractStatsResponse(
            total_agents=0,
            contract_address=client.contract_address,
            is_connected=False,
        )

    try:
        total_agents = await client.get_total_agents()
        return ContractStatsResponse(
            total_agents=total_agents,
            contract_address=client.contract_address,
            is_connected=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract call failed: {str(e)}")
