#!/usr/bin/env python3
"""
AgentFICO Score Calculator for Real ERC-8004 Agents

이 스크립트는 수집된 ERC-8004 에이전트들의 AgentFICO 점수를 계산합니다.

점수 계산 공식 (ADR-002):
    overall = (txSuccess × 0.40 + x402Profitability × 0.40 + erc8004Stability × 0.20) × 10

각 지표: 0-100
overall: 0-1000
"""
import asyncio
import base64
import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add api/src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "api" / "src"))

try:
    import httpx
except ImportError:
    httpx = None


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class AgentScore:
    """에이전트 점수 데이터"""
    address: str
    chain: str
    chain_id: int
    token_id: int
    name: str
    overall: int  # 0-1000
    tx_success: int  # 0-100
    x402_profitability: int  # 0-100
    erc8004_stability: int  # 0-100
    risk_level: str  # "low", "medium", "high", "very_high"
    confidence: int  # 0-100
    metadata: Dict[str, Any]


@dataclass
class ScoringResult:
    """점수 계산 결과"""
    scored_at: str
    total_scored: int
    distribution: Dict[str, Any]
    agents: List[Dict[str, Any]]


# =============================================================================
# Score Calculation Functions
# =============================================================================

def calculate_overall_score(
    tx_success: int,
    x402_profitability: int,
    erc8004_stability: int
) -> int:
    """
    ADR-002 공식에 따라 overall 점수 계산
    
    overall = (txSuccess × 0.40 + x402Profitability × 0.40 + erc8004Stability × 0.20) × 10
    """
    weighted_sum = (
        tx_success * 0.40 +
        x402_profitability * 0.40 +
        erc8004_stability * 0.20
    )
    overall = int(weighted_sum * 10)
    return min(max(overall, 0), 1000)  # Clamp to 0-1000


def determine_risk_level(overall: int) -> str:
    """overall 점수에 따라 위험 수준 결정"""
    if overall >= 800:
        return "low"
    elif overall >= 600:
        return "medium"
    elif overall >= 400:
        return "high"
    else:
        return "very_high"


def determine_tier(overall: int) -> str:
    """overall 점수에 따라 tier 결정"""
    if overall >= 800:
        return "excellent"
    elif overall >= 650:
        return "good"
    elif overall >= 500:
        return "average"
    elif overall >= 350:
        return "below_average"
    else:
        return "poor"


def parse_metadata_url(url: str) -> Dict[str, Any]:
    """메타데이터 URL에서 JSON 파싱"""
    if not url:
        return {}
    
    # data: URI 처리
    if url.startswith("data:application/json"):
        try:
            if ";base64," in url:
                b64_data = url.split(";base64,")[1]
                json_str = base64.b64decode(b64_data).decode("utf-8")
            else:
                json_str = url.split(",", 1)[1]
            return json.loads(json_str)
        except Exception as e:
            print(f"  [WARN] Failed to parse data URI: {e}")
            return {}
    
    # IPFS 또는 HTTP URI는 나중에 fetch 필요
    return {"_uri": url}


def calculate_erc8004_stability(
    metadata: Dict[str, Any],
    has_agent_wallet: bool,
    token_id: int
) -> tuple[int, int]:
    """
    ERC-8004 메타데이터 기반 stability 점수 계산
    
    Score breakdown (total 100 points):
    - Registration: 20 points (registered in ERC-8004)
    - Metadata completeness: 30 points
    - Services/Endpoints: 20 points
    - x402 support: 15 points
    - Active status: 15 points
    
    Returns:
        tuple: (stability_score, confidence)
    """
    score = 0
    data_points = 0
    
    # 1. Registration (20 points) - ERC-8004 등록됨
    score += 20
    data_points += 1
    
    # 2. Metadata completeness (30 points)
    metadata_fields = ["name", "description", "image", "type"]
    filled = sum(1 for f in metadata_fields if metadata.get(f))
    metadata_score = int((filled / len(metadata_fields)) * 30)
    score += metadata_score
    if filled > 0:
        data_points += 1
    
    # 3. Services/Endpoints (20 points)
    services = metadata.get("services", []) or metadata.get("endpoints", [])
    if services:
        service_score = min(len(services) * 5, 20)  # 5점씩, 최대 20점
        score += service_score
        data_points += 1
    
    # 4. x402 Support (15 points)
    if metadata.get("x402Support", False):
        score += 15
        data_points += 1
    
    # 5. Active status (15 points)
    if metadata.get("active", True):  # Default true
        score += 15
        data_points += 1
    
    # Agent wallet 보너스 (stability 신뢰도)
    if has_agent_wallet:
        data_points += 1
    
    # Confidence 계산 (데이터 포인트 기반)
    max_data_points = 6
    confidence = int((data_points / max_data_points) * 100)
    
    return min(score, 100), confidence


def calculate_tx_success_simulated(
    agent_address: str,
    token_id: int,
    metadata: Dict[str, Any]
) -> tuple[int, int]:
    """
    트랜잭션 성공률 시뮬레이션 (테스트넷용)
    
    실제 Etherscan API가 없으므로 에이전트 특성 기반으로 시뮬레이션합니다.
    - x402 지원 에이전트: 더 높은 트랜잭션 활동 예상
    - 서비스가 많은 에이전트: 더 많은 상호작용 예상
    
    Returns:
        tuple: (tx_success_score, confidence)
    """
    # 주소 기반 결정적 시드
    seed = int(hashlib.sha256(agent_address.lower().encode()).hexdigest()[:8], 16)
    
    # 기본 점수 (50-80 범위)
    base_score = 50 + (seed % 31)
    
    # 메타데이터 기반 조정
    adjustments = 0
    
    # x402 지원 시 +10
    if metadata.get("x402Support"):
        adjustments += 10
    
    # 서비스가 많을수록 +5 (최대 15)
    services = metadata.get("services", []) or metadata.get("endpoints", [])
    adjustments += min(len(services) * 3, 15)
    
    # active 상태 +5
    if metadata.get("active", True):
        adjustments += 5
    
    tx_success = min(base_score + adjustments, 100)
    
    # 테스트넷이므로 confidence는 낮음 (40-60)
    confidence = 40 + (seed % 21)
    
    return tx_success, confidence


def calculate_x402_profitability(
    agent_address: str,
    metadata: Dict[str, Any]
) -> tuple[int, int]:
    """
    x402 Profitability 계산
    
    x402 데이터가 없으므로:
    - x402 지원 에이전트: 메타데이터 기반 시뮬레이션
    - 미지원 에이전트: 기본값 50 사용
    
    Returns:
        tuple: (profitability_score, confidence)
    """
    if not metadata.get("x402Support"):
        # x402 미지원: 기본값 50, 매우 낮은 confidence
        return 50, 20
    
    # x402 지원 에이전트: 시뮬레이션
    seed = int(hashlib.sha256(agent_address.lower().encode()).hexdigest()[:8], 16)
    
    # x402 지원 에이전트는 더 높은 수익성 기대 (55-85 범위)
    base_score = 55 + (seed % 31)
    
    # 서비스 수에 따른 조정
    services = metadata.get("services", []) or metadata.get("endpoints", [])
    service_bonus = min(len(services) * 2, 10)
    
    profitability = min(base_score + service_bonus, 100)
    
    # x402 데이터 없으므로 confidence는 중간 수준
    confidence = 35 + (seed % 16)
    
    return profitability, confidence


# =============================================================================
# Main Scoring Logic
# =============================================================================

def score_single_agent(agent_data: Dict[str, Any]) -> AgentScore:
    """단일 에이전트 점수 계산"""
    address = agent_data.get("agent_wallet") or agent_data.get("owner", "")
    chain = agent_data.get("chain", "unknown")
    chain_id = agent_data.get("chain_id", 0)
    token_id = agent_data.get("token_id", 0)
    
    # 메타데이터 파싱
    metadata_url = agent_data.get("metadata_url", "")
    metadata = parse_metadata_url(metadata_url)
    
    name = metadata.get("name", f"Agent #{token_id}")
    has_agent_wallet = agent_data.get("agent_wallet") is not None
    
    print(f"  Scoring: {name} (token #{token_id}) on {chain}")
    
    # 각 지표 계산
    erc8004_stability, stability_conf = calculate_erc8004_stability(
        metadata, has_agent_wallet, token_id
    )
    
    tx_success, tx_conf = calculate_tx_success_simulated(
        address, token_id, metadata
    )
    
    x402_profitability, x402_conf = calculate_x402_profitability(
        address, metadata
    )
    
    # Overall 점수 계산
    overall = calculate_overall_score(tx_success, x402_profitability, erc8004_stability)
    
    # 위험 수준 결정
    risk_level = determine_risk_level(overall)
    
    # 전체 confidence (가중 평균)
    confidence = int(
        tx_conf * 0.40 +
        x402_conf * 0.40 +
        stability_conf * 0.20
    )
    
    print(f"    -> Overall: {overall}/1000, Risk: {risk_level}, Confidence: {confidence}%")
    print(f"       txSuccess: {tx_success}, x402: {x402_profitability}, stability: {erc8004_stability}")
    
    return AgentScore(
        address=address.lower() if address else "",
        chain=chain,
        chain_id=chain_id,
        token_id=token_id,
        name=name,
        overall=overall,
        tx_success=tx_success,
        x402_profitability=x402_profitability,
        erc8004_stability=erc8004_stability,
        risk_level=risk_level,
        confidence=confidence,
        metadata={
            "x402_support": metadata.get("x402Support", False),
            "services_count": len(metadata.get("services", []) or metadata.get("endpoints", [])),
            "active": metadata.get("active", True),
            "description": metadata.get("description", "")[:100] if metadata.get("description") else None
        }
    )


def calculate_distribution(agents: List[AgentScore]) -> Dict[str, Any]:
    """점수 분포 통계 계산"""
    if not agents:
        return {
            "average": 0,
            "min": 0,
            "max": 0,
            "median": 0,
            "std_dev": 0,
            "tiers": {
                "excellent": 0,
                "good": 0,
                "average": 0,
                "below_average": 0,
                "poor": 0
            }
        }
    
    scores = [a.overall for a in agents]
    
    # 기본 통계
    avg = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)
    
    # 중앙값
    sorted_scores = sorted(scores)
    mid = len(sorted_scores) // 2
    if len(sorted_scores) % 2 == 0:
        median = (sorted_scores[mid - 1] + sorted_scores[mid]) / 2
    else:
        median = sorted_scores[mid]
    
    # 표준편차
    variance = sum((s - avg) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5
    
    # Tier 분포
    tiers = {
        "excellent": 0,  # >= 800
        "good": 0,       # 650-799
        "average": 0,    # 500-649
        "below_average": 0,  # 350-499
        "poor": 0        # < 350
    }
    
    for score in scores:
        tier = determine_tier(score)
        tiers[tier] += 1
    
    return {
        "average": int(avg),
        "min": min_score,
        "max": max_score,
        "median": int(median),
        "std_dev": round(std_dev, 2),
        "tiers": tiers
    }


def main():
    """메인 실행 함수"""
    # 경로 설정
    base_dir = Path(__file__).parent.parent
    input_path = base_dir / "data" / "agents" / "real-agents.json"
    output_path = base_dir / "data" / "agents" / "scored-agents.json"
    
    print("=" * 60)
    print("AgentFICO Score Calculator for ERC-8004 Agents")
    print("=" * 60)
    
    # 입력 파일 읽기
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    with open(input_path, "r") as f:
        data = json.load(f)
    
    agents_data = data.get("agents", [])
    print(f"\nLoaded {len(agents_data)} agents from {input_path.name}")
    print(f"Collection date: {data.get('collected_at', 'unknown')}")
    print()
    
    # 각 에이전트 점수 계산
    print("Calculating scores...")
    print("-" * 40)
    
    scored_agents: List[AgentScore] = []
    for agent_data in agents_data:
        try:
            score = score_single_agent(agent_data)
            scored_agents.append(score)
        except Exception as e:
            print(f"  [ERROR] Failed to score agent: {e}")
            continue
    
    print("-" * 40)
    print(f"\nSuccessfully scored {len(scored_agents)} agents")
    
    # 분포 계산
    distribution = calculate_distribution(scored_agents)
    
    print("\n📊 Score Distribution:")
    print(f"   Average: {distribution['average']}/1000")
    print(f"   Min: {distribution['min']}, Max: {distribution['max']}")
    print(f"   Median: {distribution['median']}")
    print(f"   Std Dev: {distribution['std_dev']}")
    print("\n📈 Tier Distribution:")
    for tier, count in distribution['tiers'].items():
        print(f"   {tier.replace('_', ' ').title()}: {count}")
    
    # 결과 생성
    result = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "scoring_version": "1.0.0",
        "formula": "overall = (txSuccess × 0.40 + x402Profitability × 0.40 + erc8004Stability × 0.20) × 10",
        "source": {
            "file": input_path.name,
            "collected_at": data.get("collected_at", "unknown"),
            "chains": list(data.get("chains", {}).keys())
        },
        "total_scored": len(scored_agents),
        "distribution": distribution,
        "agents": [
            {
                "address": a.address,
                "chain": a.chain,
                "chain_id": a.chain_id,
                "token_id": a.token_id,
                "name": a.name,
                "overall": a.overall,
                "tx_success": a.tx_success,
                "x402_profitability": a.x402_profitability,
                "erc8004_stability": a.erc8004_stability,
                "risk_level": a.risk_level,
                "confidence": a.confidence,
                "tier": determine_tier(a.overall),
                "metadata": a.metadata
            }
            for a in sorted(scored_agents, key=lambda x: x.overall, reverse=True)
        ]
    }
    
    # 출력 파일 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()
