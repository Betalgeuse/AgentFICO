"""
AgentFICO 시나리오 테스트

전체 플로우:
1. Score Calculator로 점수 계산
2. Contract에 점수 업데이트
3. 점수 조회 및 검증
4. 리스크 평가
"""
import pytest
import os
import sys

# 환경 변수 설정 (테스트용)
os.environ.setdefault("RPC_URL", "http://127.0.0.1:8545")
os.environ.setdefault("CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
os.environ.setdefault("OWNER_PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")

# 프로젝트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


# 테스트용 에이전트 주소
TEST_AGENT_1 = "0x1111111111111111111111111111111111111111"
TEST_AGENT_2 = "0x2222222222222222222222222222222222222222"
TEST_AGENT_3 = "0x3333333333333333333333333333333333333333"


class TestScenario1_ScoreUpdate:
    """시나리오 1: 점수 업데이트 플로우"""
    
    @pytest.mark.anyio
    async def test_update_and_verify_score(self):
        """점수 업데이트 후 조회 검증"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. 점수 업데이트
            update_response = await client.post(
                f"/v1/contract/score/{TEST_AGENT_1}",
                json={
                    "tx_success": 90,
                    "x402_profitability": 85,
                    "erc8004_stability": 80,
                    "confidence": 95,
                    "risk_level": "low",
                    "ipfs_breakdown": ""
                }
            )
            # 로컬 노드 없으면 스킵
            if update_response.status_code == 500:
                pytest.skip("Anvil not running")
            
            assert update_response.status_code == 200
            assert "tx_hash" in update_response.json()
            
            # 2. 점수 조회
            get_response = await client.get(f"/v1/contract/score/{TEST_AGENT_1}")
            assert get_response.status_code == 200
            
            score = get_response.json()
            # overall = (90*0.4 + 85*0.4 + 80*0.2) * 10 = 860
            assert score["overall"] == 860
            assert score["txSuccess"] == 90
    
    @pytest.mark.anyio
    async def test_registration_status(self):
        """등록 상태 확인"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 등록된 에이전트
            response = await client.get(f"/v1/contract/registered/{TEST_AGENT_1}")
            if response.status_code == 500:
                pytest.skip("Anvil not running")
            
            assert response.status_code == 200


class TestScenario2_RiskAssessment:
    """시나리오 2: 리스크 평가 플로우"""
    
    @pytest.mark.anyio
    async def test_risk_assessment_lending(self):
        """Lending 프로토콜 리스크 평가"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/v1/contract/risk/{TEST_AGENT_1}",
                params={"amount_usdc": 10000, "protocol_type": "lending"}
            )
            if response.status_code == 500:
                pytest.skip("Anvil not running or agent not registered")
            
            assert response.status_code == 200
            risk = response.json()
            assert "riskLevel" in risk


class TestScenario3_ContractStats:
    """시나리오 3: 컨트랙트 통계"""
    
    @pytest.mark.anyio
    async def test_get_contract_stats(self):
        """통계 조회"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/contract/stats")
            if response.status_code == 500:
                pytest.skip("Anvil not running")
            
            assert response.status_code == 200
            stats = response.json()
            assert "total_agents" in stats
            assert "contract_address" in stats


class TestScenario4_ErrorHandling:
    """시나리오 4: 에러 핸들링"""
    
    @pytest.mark.anyio
    async def test_invalid_score_range(self):
        """잘못된 점수 범위 - Pydantic 검증"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/v1/contract/score/{TEST_AGENT_1}",
                json={
                    "tx_success": 150,  # > 100 (invalid)
                    "x402_profitability": 85,
                    "erc8004_stability": 80,
                    "confidence": 95,
                    "risk_level": "low",
                    "ipfs_breakdown": ""
                }
            )
            # Pydantic 검증 에러
            assert response.status_code == 422
