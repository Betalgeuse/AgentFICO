#!/usr/bin/env python3
"""
ERC-8004 에이전트 수집 스크립트

Ethereum Sepolia와 Base Sepolia에서 등록된 에이전트 주소를 수집합니다.
"""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from typing import Optional

from web3 import AsyncWeb3, AsyncHTTPProvider

# 프로젝트 루트
project_root = Path(__file__).parent.parent


class Chain(str, Enum):
    SEPOLIA = "sepolia"
    BASE_SEPOLIA = "base-sepolia"


# ERC-8004 Identity Registry 공식 배포 주소
REGISTRY_ADDRESSES = {
    Chain.SEPOLIA: "0xf66e7CBdAE1Cb710fee7732E4e1f173624e137A7",
    Chain.BASE_SEPOLIA: "0xdc527768082c489e0ee228d24d3cfa290214f387",
}

# 컨트랙트 배포 블록
DEPLOYMENT_BLOCKS = {
    Chain.SEPOLIA: 7500000,
    Chain.BASE_SEPOLIA: 20000000,
}

# RPC URLs
RPC_URLS = {
    Chain.SEPOLIA: "https://ethereum-sepolia-rpc.publicnode.com",
    Chain.BASE_SEPOLIA: "https://base-sepolia-rpc.publicnode.com",
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

# ERC-721 + ERC-8004 ABI
IDENTITY_REGISTRY_ABI = [
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


class ERC8004Collector:
    """ERC-8004 에이전트 수집기"""
    
    def __init__(self, chain: Chain):
        self.chain = chain
        self.rpc_url = RPC_URLS[chain]
        self.registry_address = REGISTRY_ADDRESSES[chain]
        self._w3: Optional[AsyncWeb3] = None
        self._contract = None
    
    async def _get_web3(self) -> AsyncWeb3:
        if self._w3 is None:
            self._w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc_url))
        return self._w3
    
    async def _get_contract(self):
        if self._contract is None:
            w3 = await self._get_web3()
            self._contract = w3.eth.contract(
                address=w3.to_checksum_address(self.registry_address),
                abi=IDENTITY_REGISTRY_ABI
            )
        return self._contract
    
    async def get_valid_token_ids(self) -> list[int]:
        """Transfer 이벤트에서 유효한 토큰 ID 조회"""
        try:
            w3 = await self._get_web3()
            
            # Transfer(address,address,uint256) 이벤트 토픽
            transfer_topic = w3.keccak(text='Transfer(address,address,uint256)')
            zero_address = '0x' + '0' * 64  # 민팅은 0x0에서
            
            latest = await w3.eth.block_number
            deployment_block = DEPLOYMENT_BLOCKS.get(self.chain, 0)
            
            chunk_size = 45000
            max_chunks = 15
            
            token_ids = set()
            current_block = latest
            chunks_fetched = 0
            
            while current_block > deployment_block and chunks_fetched < max_chunks:
                from_block = max(deployment_block, current_block - chunk_size)
                to_block = current_block
                
                try:
                    logs = await w3.eth.get_logs({
                        'address': w3.to_checksum_address(self.registry_address),
                        'topics': [transfer_topic, zero_address],
                        'fromBlock': from_block,
                        'toBlock': to_block,
                    })
                    
                    for log in logs:
                        token_id = int(log['topics'][3].hex(), 16)
                        token_ids.add(token_id)
                    
                    print(f"  [블록 {from_block}-{to_block}] {len(logs)} mints 발견")
                    
                except Exception as chunk_err:
                    print(f"  [경고] 블록 {from_block}-{to_block} 조회 실패: {chunk_err}")
                
                current_block = from_block - 1
                chunks_fetched += 1
            
            return sorted(token_ids, reverse=True)
            
        except Exception as e:
            print(f"토큰 ID 조회 실패: {e}")
            return []
    
    async def get_owner(self, token_id: int) -> str:
        contract = await self._get_contract()
        return await contract.functions.ownerOf(token_id).call()
    
    async def get_agent_wallet(self, token_id: int) -> Optional[str]:
        try:
            contract = await self._get_contract()
            wallet = await contract.functions.getAgentWallet(token_id).call()
            if wallet == "0x0000000000000000000000000000000000000000":
                return None
            return wallet
        except:
            return None
    
    async def get_token_uri(self, token_id: int) -> str:
        contract = await self._get_contract()
        return await contract.functions.tokenURI(token_id).call()


async def collect_agents_from_chain(chain: Chain) -> dict:
    """단일 체인에서 에이전트 수집"""
    print(f"\n{'='*60}")
    print(f"[{chain.value}] 에이전트 수집 시작")
    print(f"Registry: {REGISTRY_ADDRESSES[chain]}")
    print(f"Chain ID: {CHAIN_IDS[chain]}")
    print(f"{'='*60}")
    
    client = ERC8004Collector(chain)
    
    # 유효한 토큰 ID 조회
    token_ids = await client.get_valid_token_ids()
    print(f"발견된 에이전트 수: {len(token_ids)}")
    
    if not token_ids:
        print("이 체인에서 에이전트를 찾지 못했습니다.")
        return {
            "chain": chain.value,
            "chain_id": CHAIN_IDS[chain],
            "registry_address": REGISTRY_ADDRESSES[chain],
            "explorer_url": EXPLORER_URLS[chain],
            "agent_count": 0,
            "agents": []
        }
    
    agents = []
    
    # 각 에이전트 정보 수집
    for i, token_id in enumerate(token_ids):
        try:
            print(f"[{i+1}/{len(token_ids)}] Token ID {token_id} 조회 중...")
            
            # 기본 정보 조회
            owner = await client.get_owner(token_id)
            wallet = await client.get_agent_wallet(token_id)
            uri = await client.get_token_uri(token_id)
            
            agent_data = {
                "chain": chain.value,
                "chain_id": CHAIN_IDS[chain],
                "token_id": token_id,
                "owner": owner,
                "agent_wallet": wallet,
                "metadata_url": uri,
                "explorer_link": f"{EXPLORER_URLS[chain]}/token/{REGISTRY_ADDRESSES[chain]}?a={token_id}"
            }
            
            agents.append(agent_data)
            print(f"  ✓ Owner: {owner[:10]}...{owner[-6:]}")
            if wallet:
                print(f"  ✓ Wallet: {wallet[:10]}...{wallet[-6:]}")
                
        except Exception as e:
            print(f"  ✗ 에러: {e}")
            continue
    
    return {
        "chain": chain.value,
        "chain_id": CHAIN_IDS[chain],
        "registry_address": REGISTRY_ADDRESSES[chain],
        "explorer_url": EXPLORER_URLS[chain],
        "agent_count": len(agents),
        "agents": agents
    }


async def main():
    """메인 수집 함수"""
    print("=" * 60)
    print("ERC-8004 에이전트 수집 시작")
    print(f"시작 시간: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # 두 체인에서 수집
    sepolia_result = await collect_agents_from_chain(Chain.SEPOLIA)
    base_result = await collect_agents_from_chain(Chain.BASE_SEPOLIA)
    
    # 모든 에이전트 합치기
    all_agents = sepolia_result["agents"] + base_result["agents"]
    
    # 결과 구성
    result = {
        "collected_at": datetime.utcnow().isoformat() + "Z",
        "total_count": len(all_agents),
        "chains": {
            "ethereum_sepolia": {
                "registry_address": sepolia_result["registry_address"],
                "chain_id": sepolia_result["chain_id"],
                "explorer_url": sepolia_result["explorer_url"],
                "agent_count": sepolia_result["agent_count"]
            },
            "base_sepolia": {
                "registry_address": base_result["registry_address"],
                "chain_id": base_result["chain_id"],
                "explorer_url": base_result["explorer_url"],
                "agent_count": base_result["agent_count"]
            }
        },
        "agents": all_agents
    }
    
    # JSON 파일 저장
    output_path = project_root / "data" / "agents" / "real-agents.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("수집 완료!")
    print("=" * 60)
    print(f"총 에이전트 수: {result['total_count']}")
    print(f"  - Ethereum Sepolia: {sepolia_result['agent_count']}")
    print(f"  - Base Sepolia: {base_result['agent_count']}")
    print(f"\n결과 저장 위치: {output_path}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
