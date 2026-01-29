"""AgentFICOScoreV2 Contract Client

Base Sepolia 테스트넷/메인넷 컨트랙트와 상호작용하는 클라이언트
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from web3 import Web3
from web3.exceptions import ContractLogicError


# Risk level mapping (V2 uses uint8)
RISK_LEVEL_NAMES = {
    1: "excellent",
    2: "good",
    3: "average",
    4: "below_average",
    5: "poor",
}


class ContractClient:
    """AgentFICOScoreV2 컨트랙트 클라이언트"""

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        private_key: Optional[str] = None,
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.private_key = private_key
        self.account = None

        # ABI 로드
        self.abi = self._load_abi()
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi,
        )

        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)

    def _load_abi(self) -> List[Dict[str, Any]]:
        """ABI 파일 로드"""
        # V2 ABI 경로
        abi_path = (
            Path(__file__).parent.parent.parent.parent
            / "contracts"
            / "out"
            / "AgentFICOScoreV2.sol"
            / "AgentFICOScoreV2.json"
        )

        if abi_path.exists():
            with open(abi_path) as f:
                data = json.load(f)
                return data.get("abi", [])

        # Fallback: V2 ABI 직접 정의
        return self._get_v2_abi()

    def _get_v2_abi(self) -> List[Dict[str, Any]]:
        """V2 ABI for core functions"""
        return [
            {
                "type": "function",
                "name": "getScore",
                "inputs": [{"name": "agent", "type": "address"}],
                "outputs": [
                    {
                        "name": "",
                        "type": "tuple",
                        "components": [
                            {"name": "overall", "type": "uint256"},
                            {"name": "txSuccess", "type": "uint256"},
                            {"name": "x402Profitability", "type": "uint256"},
                            {"name": "erc8004Stability", "type": "uint256"},
                            {"name": "confidence", "type": "uint256"},
                            {"name": "riskLevel", "type": "uint8"},
                            {"name": "timestamp", "type": "uint256"},
                            {"name": "antiGamingApplied", "type": "bool"},
                        ],
                    }
                ],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "getScoreOnly",
                "inputs": [{"name": "agent", "type": "address"}],
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "updateScore",
                "inputs": [
                    {"name": "agent", "type": "address"},
                    {"name": "txScore", "type": "uint256"},
                    {"name": "x402Score", "type": "uint256"},
                    {"name": "erc8004Score", "type": "uint256"},
                    {"name": "confidence", "type": "uint256"},
                    {"name": "antiGamingApplied", "type": "bool"},
                ],
                "outputs": [],
                "stateMutability": "nonpayable",
            },
            {
                "type": "function",
                "name": "batchUpdateScores",
                "inputs": [
                    {"name": "agents", "type": "address[]"},
                    {"name": "txScores", "type": "uint256[]"},
                    {"name": "x402Scores", "type": "uint256[]"},
                    {"name": "erc8004Scores", "type": "uint256[]"},
                    {"name": "confidences", "type": "uint256[]"},
                    {"name": "antiGamingFlags", "type": "bool[]"},
                ],
                "outputs": [],
                "stateMutability": "nonpayable",
            },
            {
                "type": "function",
                "name": "isRegistered",
                "inputs": [{"name": "agent", "type": "address"}],
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "totalAgents",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "assessRisk",
                "inputs": [
                    {"name": "agent", "type": "address"},
                    {"name": "amountUsdc", "type": "uint256"},
                    {"name": "protocolRiskBps", "type": "uint256"},
                ],
                "outputs": [
                    {
                        "name": "",
                        "type": "tuple",
                        "components": [
                            {"name": "riskLevel", "type": "uint256"},
                            {"name": "defaultProbability", "type": "uint256"},
                            {"name": "expectedLoss", "type": "uint256"},
                        ],
                    }
                ],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "VERSION",
                "inputs": [],
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
            },
            {
                "type": "function",
                "name": "owner",
                "inputs": [],
                "outputs": [{"name": "", "type": "address"}],
                "stateMutability": "view",
            },
        ]

    async def get_score(self, agent_address: str) -> Dict[str, Any]:
        """getScore() 호출 - 전체 점수 조회 (V2)"""
        agent = Web3.to_checksum_address(agent_address)

        try:
            result = self.contract.functions.getScore(agent).call()
            risk_level_num = result[5]
            return {
                "overall": result[0],
                "txSuccess": result[1],
                "x402Profitability": result[2],
                "erc8004Stability": result[3],
                "confidence": result[4],
                "riskLevel": RISK_LEVEL_NAMES.get(risk_level_num, "unknown"),
                "riskLevelNum": risk_level_num,
                "timestamp": result[6],
                "antiGamingApplied": result[7],
            }
        except ContractLogicError:
            raise ValueError(f"Agent not registered: {agent_address}")

    async def get_score_only(self, agent_address: str) -> int:
        """getScoreOnly() 호출 - overall만 조회"""
        agent = Web3.to_checksum_address(agent_address)
        try:
            return self.contract.functions.getScoreOnly(agent).call()
        except ContractLogicError:
            raise ValueError(f"Agent not registered: {agent_address}")

    async def update_score(
        self,
        agent_address: str,
        tx_success: int,
        x402_profitability: int,
        erc8004_stability: int,
        confidence: int,
        anti_gaming_applied: bool = True,
    ) -> str:
        """updateScore() 호출 - 점수 업데이트 (owner only, V2)"""
        if not self.private_key or not self.account:
            raise ValueError("Private key required for write operations")

        agent = Web3.to_checksum_address(agent_address)

        # 트랜잭션 빌드
        tx = self.contract.functions.updateScore(
            agent,
            tx_success,
            x402_profitability,
            erc8004_stability,
            confidence,
            anti_gaming_applied,
        ).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        # 서명 및 전송
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # 영수증 대기
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return receipt["transactionHash"].hex()

    async def batch_update_scores(
        self,
        agents: List[str],
        tx_scores: List[int],
        x402_scores: List[int],
        erc8004_scores: List[int],
        confidences: List[int],
        anti_gaming_flags: List[bool],
    ) -> str:
        """batchUpdateScores() 호출 - 배치 업데이트 (owner only, V2)"""
        if not self.private_key or not self.account:
            raise ValueError("Private key required for write operations")

        agents_checksummed = [Web3.to_checksum_address(a) for a in agents]

        tx = self.contract.functions.batchUpdateScores(
            agents_checksummed,
            tx_scores,
            x402_scores,
            erc8004_scores,
            confidences,
            anti_gaming_flags,
        ).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "gas": 100000 + 150000 * len(agents),  # Base + per agent
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return receipt["transactionHash"].hex()

    async def is_registered(self, agent_address: str) -> bool:
        """isRegistered() 호출"""
        agent = Web3.to_checksum_address(agent_address)
        return self.contract.functions.isRegistered(agent).call()

    async def get_total_agents(self) -> int:
        """totalAgents() 호출 (V2)"""
        return self.contract.functions.totalAgents().call()

    async def assess_risk(
        self,
        agent_address: str,
        amount_usdc: int,
        protocol_risk_bps: int = 0,
    ) -> Dict[str, Any]:
        """assessRisk() 호출 (V2 - protocolRiskBps 사용)"""
        agent = Web3.to_checksum_address(agent_address)

        try:
            result = self.contract.functions.assessRisk(
                agent, amount_usdc, protocol_risk_bps
            ).call()

            return {
                "riskLevel": result[0],
                "defaultProbability": result[1],
                "expectedLoss": result[2],
            }
        except ContractLogicError:
            raise ValueError(f"Agent not registered: {agent_address}")

    async def get_version(self) -> int:
        """VERSION() 호출"""
        return self.contract.functions.VERSION().call()

    async def get_owner(self) -> str:
        """owner() 호출"""
        return self.contract.functions.owner().call()

    def is_connected(self) -> bool:
        """Check if connected to RPC"""
        return self.w3.is_connected()
