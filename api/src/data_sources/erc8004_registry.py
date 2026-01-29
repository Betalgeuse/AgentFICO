"""
ERC-8004 Identity Registry Client

온체인에서 ERC-8004 에이전트 목록을 조회합니다.
"""
import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import httpx
from web3 import AsyncWeb3, AsyncHTTPProvider

logger = logging.getLogger(__name__)


class Chain(str, Enum):
    SEPOLIA = "sepolia"
    BASE_SEPOLIA = "base-sepolia"


# ERC-8004 Identity Registry 공식 배포 주소 (ChaosChain Reference Implementation)
# https://github.com/ChaosChain/trustless-agents-erc-ri/blob/main/deployments.json
REGISTRY_ADDRESSES = {
    Chain.SEPOLIA: "0xf66e7CBdAE1Cb710fee7732E4e1f173624e137A7",  # v1.2.0 (Jan 2026)
    Chain.BASE_SEPOLIA: "0xdc527768082c489e0ee228d24d3cfa290214f387",  # v1.1.0 (Legacy)
}

# 컨트랙트 배포 블록 (이벤트 조회 시작점)
DEPLOYMENT_BLOCKS = {
    Chain.SEPOLIA: 7500000,  # ~2026-01 배포 추정
    Chain.BASE_SEPOLIA: 20000000,  # ~2026-01 배포 추정
}

# RPC URLs (public endpoints)
RPC_URLS = {
    Chain.SEPOLIA: "https://ethereum-sepolia-rpc.publicnode.com",
    Chain.BASE_SEPOLIA: "https://base-sepolia-rpc.publicnode.com",  # More reliable than sepolia.base.org
}

# Chain IDs
CHAIN_IDS = {
    Chain.SEPOLIA: 11155111,
    Chain.BASE_SEPOLIA: 84532,
}

# Block explorer URLs
EXPLORER_URLS = {
    Chain.SEPOLIA: "https://sepolia.etherscan.io",
    Chain.BASE_SEPOLIA: "https://sepolia.basescan.org",
}

# ERC-721 + ERC-8004 ABI (필요한 함수만)
IDENTITY_REGISTRY_ABI = [
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getAgentWallet",
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


@dataclass
class AgentMetadata:
    """ERC-8004 에이전트 메타데이터"""
    agent_id: int
    name: str
    description: str
    image: Optional[str]
    owner: str
    agent_wallet: Optional[str]
    chain: str
    chain_id: int
    services: list[dict]
    x402_support: bool
    active: bool
    raw_uri: str
    fetched_at: datetime


@dataclass
class AgentListResponse:
    """에이전트 목록 응답"""
    agents: list[AgentMetadata]
    total: int
    has_more: bool
    chain: str


class ERC8004RegistryClient:
    """ERC-8004 Identity Registry 클라이언트"""
    
    def __init__(self, chain: Chain = Chain.SEPOLIA):
        self.chain = chain
        self.rpc_url = RPC_URLS[chain]
        self.registry_address = REGISTRY_ADDRESSES[chain]
        self.chain_id = CHAIN_IDS[chain]
        
        # Web3 인스턴스
        self._w3: Optional[AsyncWeb3] = None
        self._contract = None
        
        # 캐시 (1분)
        self._cache: dict = {}
        self._cache_ttl = timedelta(minutes=1)
    
    async def _get_web3(self) -> AsyncWeb3:
        """Web3 인스턴스 반환 (lazy initialization)"""
        if self._w3 is None:
            self._w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc_url))
        return self._w3
    
    async def _get_contract(self):
        """컨트랙트 인스턴스 반환"""
        if self._contract is None:
            w3 = await self._get_web3()
            self._contract = w3.eth.contract(
                address=w3.to_checksum_address(self.registry_address),
                abi=IDENTITY_REGISTRY_ABI
            )
        return self._contract
    
    def _get_cache(self, key: str):
        """캐시에서 값 가져오기"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                return value
            del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value):
        """캐시에 값 저장"""
        self._cache[key] = (value, datetime.now())
    
    async def get_valid_token_ids(self) -> list[int]:
        """이벤트 로그에서 유효한 토큰 ID 목록 조회
        
        RPC의 블록 범위 제한(보통 50,000블록)을 고려하여 청크 단위로 조회합니다.
        """
        cache_key = f"{self.chain}:valid_token_ids"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            w3 = await self._get_web3()
            
            # Transfer 이벤트로 민팅된 토큰 ID 찾기
            transfer_topic = w3.keccak(text='Transfer(address,address,uint256)')
            zero_address = '0x' + '0' * 64  # 민팅은 0x0에서 전송
            
            latest = await w3.eth.block_number
            deployment_block = DEPLOYMENT_BLOCKS.get(self.chain, 0)
            
            # RPC 제한: 보통 50,000 블록 제한이 있음
            # 청크 단위로 조회 (최대 10개 청크)
            chunk_size = 45000  # 안전하게 45,000
            max_chunks = 10
            
            token_ids = set()
            current_block = latest
            chunks_fetched = 0
            
            while current_block > deployment_block and chunks_fetched < max_chunks:
                from_block = max(deployment_block, current_block - chunk_size)
                to_block = current_block
                
                try:
                    logs = await w3.eth.get_logs({
                        'address': w3.to_checksum_address(self.registry_address),
                        'topics': [transfer_topic, zero_address],  # from = 0x0 (mint)
                        'fromBlock': from_block,
                        'toBlock': to_block,
                    })
                    
                    for log in logs:
                        token_id = int(log['topics'][3].hex(), 16)
                        token_ids.add(token_id)
                    
                    logger.debug(f"[{self.chain}] Blocks {from_block}-{to_block}: {len(logs)} mints")
                    
                except Exception as chunk_err:
                    logger.warning(f"[{self.chain}] Failed to fetch blocks {from_block}-{to_block}: {chunk_err}")
                
                current_block = from_block - 1
                chunks_fetched += 1
            
            result = sorted(token_ids, reverse=True)
            
            if result:
                logger.info(f"[{self.chain}] Found {len(result)} agents: {result[:10]}...")
            else:
                logger.warning(f"[{self.chain}] No agents found in event logs")
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get token IDs from events: {e}")
            # 폴백: 빈 리스트 반환
            return []
    
    async def get_total_agents(self) -> int:
        """전체 에이전트 수 조회"""
        valid_ids = await self.get_valid_token_ids()
        return len(valid_ids)
    
    async def get_owner(self, agent_id: int) -> str:
        """에이전트 소유자 주소 조회"""
        try:
            contract = await self._get_contract()
            owner = await contract.functions.ownerOf(agent_id).call()
            return owner
        except Exception as e:
            logger.error(f"Failed to get owner for agent {agent_id}: {e}")
            raise
    
    async def get_agent_wallet(self, agent_id: int) -> Optional[str]:
        """에이전트 지갑 주소 조회"""
        try:
            contract = await self._get_contract()
            wallet = await contract.functions.getAgentWallet(agent_id).call()
            if wallet == "0x0000000000000000000000000000000000000000":
                return None
            return wallet
        except Exception:
            return None
    
    async def get_token_uri(self, agent_id: int) -> str:
        """에이전트 메타데이터 URI 조회"""
        try:
            contract = await self._get_contract()
            uri = await contract.functions.tokenURI(agent_id).call()
            return uri
        except Exception as e:
            logger.error(f"Failed to get tokenURI for agent {agent_id}: {e}")
            raise
    
    async def _fetch_metadata_from_uri(self, uri: str) -> dict:
        """URI에서 메타데이터 JSON 가져오기"""
        # data: URI 처리
        if uri.startswith("data:application/json"):
            try:
                if ";base64," in uri:
                    import base64
                    b64_data = uri.split(";base64,")[1]
                    json_str = base64.b64decode(b64_data).decode("utf-8")
                else:
                    json_str = uri.split(",", 1)[1]
                return json.loads(json_str)
            except Exception as e:
                logger.error(f"Failed to parse data URI: {e}")
                return {}
        
        # IPFS URI 처리
        if uri.startswith("ipfs://"):
            uri = f"https://ipfs.io/ipfs/{uri[7:]}"
        
        # HTTP(S) fetch
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(uri)
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch metadata from {uri}: {e}")
        
        return {}
    
    async def get_agent_metadata(self, agent_id: int) -> Optional[AgentMetadata]:
        """에이전트 메타데이터 조회"""
        cache_key = f"{self.chain}:agent:{agent_id}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 병렬로 온체인 데이터 조회
            owner, wallet, uri = await asyncio.gather(
                self.get_owner(agent_id),
                self.get_agent_wallet(agent_id),
                self.get_token_uri(agent_id),
            )
            
            # 메타데이터 fetch
            metadata = await self._fetch_metadata_from_uri(uri)
            
            # AgentMetadata 구성
            agent = AgentMetadata(
                agent_id=agent_id,
                name=metadata.get("name", f"Agent #{agent_id}"),
                description=metadata.get("description", ""),
                image=metadata.get("image"),
                owner=owner,
                agent_wallet=wallet,
                chain=self.chain.value,
                chain_id=self.chain_id,
                services=metadata.get("services", []),
                x402_support=metadata.get("x402Support", False),
                active=metadata.get("active", True),
                raw_uri=uri,
                fetched_at=datetime.now(),
            )
            
            self._set_cache(cache_key, agent)
            return agent
            
        except Exception as e:
            logger.error(f"Failed to get agent metadata for {agent_id}: {e}")
            return None
    
    async def list_agents(
        self,
        limit: int = 12,
        offset: int = 0,
        newest_first: bool = True,
    ) -> AgentListResponse:
        """에이전트 목록 조회 (페이지네이션)"""
        valid_ids = await self.get_valid_token_ids()
        total = len(valid_ids)
        
        if total == 0:
            return AgentListResponse(
                agents=[],
                total=0,
                has_more=False,
                chain=self.chain.value,
            )
        
        # 유효한 ID 목록에서 페이지네이션
        if not newest_first:
            valid_ids = list(reversed(valid_ids))
        
        # offset과 limit 적용
        paged_ids = valid_ids[offset:offset + limit]
        
        # 병렬로 메타데이터 조회
        tasks = [self.get_agent_metadata(aid) for aid in paged_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        agents = []
        for result in results:
            if isinstance(result, AgentMetadata):
                agents.append(result)
        
        has_more = (offset + len(agents)) < total
        
        return AgentListResponse(
            agents=agents,
            total=total,
            has_more=has_more,
            chain=self.chain.value,
        )


# 싱글톤 클라이언트 인스턴스
_clients: dict[Chain, ERC8004RegistryClient] = {}


def get_registry_client(chain: Chain = Chain.SEPOLIA) -> ERC8004RegistryClient:
    """Registry 클라이언트 인스턴스 반환"""
    if chain not in _clients:
        _clients[chain] = ERC8004RegistryClient(chain)
    return _clients[chain]


async def list_all_agents(
    limit: int = 12,
    offset: int = 0,
    chain: Optional[Chain] = None,
) -> AgentListResponse:
    """
    모든 체인에서 에이전트 목록 조회
    
    chain이 None이면 모든 체인에서 조회 (Sepolia + Base Sepolia)
    """
    if chain is not None:
        client = get_registry_client(chain)
        return await client.list_agents(limit=limit, offset=offset)
    
    # 모든 체인에서 조회
    sepolia_client = get_registry_client(Chain.SEPOLIA)
    base_client = get_registry_client(Chain.BASE_SEPOLIA)
    
    sepolia_result, base_result = await asyncio.gather(
        sepolia_client.list_agents(limit=limit, offset=offset),
        base_client.list_agents(limit=limit, offset=offset),
        return_exceptions=True,
    )
    
    agents = []
    total = 0
    
    if isinstance(sepolia_result, AgentListResponse):
        agents.extend(sepolia_result.agents)
        total += sepolia_result.total
    
    if isinstance(base_result, AgentListResponse):
        agents.extend(base_result.agents)
        total += base_result.total
    
    # agent_id 기준 정렬 (최신순)
    agents.sort(key=lambda a: a.agent_id, reverse=True)
    
    # limit 적용
    agents = agents[:limit]
    
    return AgentListResponse(
        agents=agents,
        total=total,
        has_more=offset + len(agents) < total,
        chain="all",
    )
