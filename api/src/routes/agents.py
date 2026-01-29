"""
ERC-8004 에이전트 목록 API 엔드포인트
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..data_sources.erc8004_registry import (
    Chain,
    get_registry_client,
    list_all_agents,
)

router = APIRouter(prefix="/agents", tags=["agents"])


class ServiceResponse(BaseModel):
    name: str
    endpoint: str
    version: Optional[str] = None


class AgentResponse(BaseModel):
    agentId: int
    name: str
    description: str
    image: Optional[str]
    owner: str
    agentWallet: Optional[str]
    chain: str
    chainId: int
    services: list[dict]
    x402Support: bool
    active: bool
    fetchedAt: str
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int
    hasMore: bool
    chain: str


def _agent_to_response(agent) -> AgentResponse:
    """AgentMetadata를 AgentResponse로 변환"""
    return AgentResponse(
        agentId=agent.agent_id,
        name=agent.name,
        description=agent.description,
        image=agent.image,
        owner=agent.owner,
        agentWallet=agent.agent_wallet,
        chain=agent.chain,
        chainId=agent.chain_id,
        services=agent.services,
        x402Support=agent.x402_support,
        active=agent.active,
        fetchedAt=agent.fetched_at.isoformat(),
    )


@router.get("", response_model=AgentListResponse)
async def get_agents(
    chain: Optional[str] = Query(
        None, 
        description="Chain filter: sepolia, base-sepolia, or null for all"
    ),
    limit: int = Query(12, ge=1, le=100, description="Number of agents to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    ERC-8004 에이전트 목록 조회
    
    온체인 Identity Registry에서 에이전트 목록을 가져옵니다.
    """
    try:
        # chain 파라미터 파싱
        chain_enum = None
        if chain:
            chain_lower = chain.lower().replace("_", "-")
            if chain_lower == "sepolia":
                chain_enum = Chain.SEPOLIA
            elif chain_lower in ("base-sepolia", "basesepolia"):
                chain_enum = Chain.BASE_SEPOLIA
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid chain: {chain}. Use 'sepolia' or 'base-sepolia'"
                )
        
        # 에이전트 목록 조회
        result = await list_all_agents(
            limit=limit,
            offset=offset,
            chain=chain_enum,
        )
        
        # 응답 변환
        agents = [_agent_to_response(a) for a in result.agents]
        
        return AgentListResponse(
            agents=agents,
            total=result.total,
            hasMore=result.has_more,
            chain=result.chain,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    chain: str = Query("sepolia", description="Chain: sepolia or base-sepolia"),
):
    """
    특정 에이전트 상세 정보 조회
    """
    try:
        chain_lower = chain.lower().replace("_", "-")
        if chain_lower == "sepolia":
            chain_enum = Chain.SEPOLIA
        elif chain_lower in ("base-sepolia", "basesepolia"):
            chain_enum = Chain.BASE_SEPOLIA
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid chain: {chain}"
            )
        
        client = get_registry_client(chain_enum)
        agent = await client.get_agent_metadata(agent_id)
        
        if agent is None:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found on {chain}"
            )
        
        return _agent_to_response(agent)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agent: {str(e)}"
        )


@router.get("/stats/summary")
async def get_agents_stats():
    """
    에이전트 통계 요약
    """
    try:
        sepolia_client = get_registry_client(Chain.SEPOLIA)
        base_client = get_registry_client(Chain.BASE_SEPOLIA)
        
        import asyncio
        sepolia_total, base_total = await asyncio.gather(
            sepolia_client.get_total_agents(),
            base_client.get_total_agents(),
            return_exceptions=True,
        )
        
        sepolia_count = sepolia_total if isinstance(sepolia_total, int) else 0
        base_count = base_total if isinstance(base_total, int) else 0
        
        return {
            "totalAgents": sepolia_count + base_count,
            "byChain": {
                "sepolia": sepolia_count,
                "base-sepolia": base_count,
            },
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stats: {str(e)}"
        )
