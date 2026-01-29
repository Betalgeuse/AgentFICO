"""Sample agent data for backtest validation.

Provides test agents with various score profiles to validate
the AgentFICO scoring formula and weight sensitivity.

Score Tiers (based on overall score 0-1000):
- EXCELLENT: 850+
- GOOD: 750-849
- AVERAGE: 650-749
- BELOW_AVERAGE: 550-649
- POOR: <550
"""

from typing import Dict, Any


# Type alias for agent data
AgentData = Dict[str, Any]

SAMPLE_AGENTS: Dict[str, AgentData] = {
    # 1. 우수한 에이전트 (예상: 850+)
    "excellent_trader": {
        "address": "0x1111111111111111111111111111111111111111",
        "description": "High success rate, profitable, well-registered",
        "expected_tier": "EXCELLENT",
        "mock_scores": {
            "tx_success": 95,
            "x402_profitability": 90,
            "erc8004_stability": 85,
        },
    },
    # 2. 좋은 에이전트 (예상: 750-849)
    "good_analyst": {
        "address": "0x2222222222222222222222222222222222222222",
        "description": "Good overall performance",
        "expected_tier": "GOOD",
        "mock_scores": {
            "tx_success": 80,
            "x402_profitability": 75,
            "erc8004_stability": 70,
        },
    },
    # 3. 평균 에이전트 (예상: 650-749)
    "average_bot": {
        "address": "0x3333333333333333333333333333333333333333",
        "description": "Average performance",
        "expected_tier": "AVERAGE",
        "mock_scores": {
            "tx_success": 70,
            "x402_profitability": 65,
            "erc8004_stability": 60,
        },
    },
    # 4. 평균 이하 에이전트 (예상: 550-649)
    "struggling_agent": {
        "address": "0x4444444444444444444444444444444444444444",
        "description": "Below average, needs improvement",
        "expected_tier": "BELOW_AVERAGE",
        "mock_scores": {
            "tx_success": 55,
            "x402_profitability": 60,
            "erc8004_stability": 50,
        },
    },
    # 5. 저조한 에이전트 (예상: <550)
    "risky_agent": {
        "address": "0x5555555555555555555555555555555555555555",
        "description": "High risk, low performance",
        "expected_tier": "POOR",
        "mock_scores": {
            "tx_success": 40,
            "x402_profitability": 35,
            "erc8004_stability": 30,
        },
    },
    # 엣지 케이스들
    "tx_specialist": {
        "address": "0x6666666666666666666666666666666666666666",
        "description": "Great tx success, poor profitability",
        "expected_tier": "AVERAGE",  # 40% weight 균형
        "mock_scores": {
            "tx_success": 95,
            "x402_profitability": 30,
            "erc8004_stability": 70,
        },
    },
    "profitable_but_risky": {
        "address": "0x7777777777777777777777777777777777777777",
        "description": "High profit but low tx success",
        "expected_tier": "AVERAGE",
        "mock_scores": {
            "tx_success": 40,
            "x402_profitability": 95,
            "erc8004_stability": 60,
        },
    },
    "new_agent": {
        "address": "0x8888888888888888888888888888888888888888",
        "description": "New agent, limited history",
        "expected_tier": "BELOW_AVERAGE",
        "mock_scores": {
            "tx_success": 60,
            "x402_profitability": 50,
            "erc8004_stability": 20,  # 미등록
        },
    },
}


def get_agents_by_tier(tier: str) -> Dict[str, AgentData]:
    """Filter agents by expected tier.

    Args:
        tier: Expected tier name (EXCELLENT, GOOD, AVERAGE, BELOW_AVERAGE, POOR)

    Returns:
        Dictionary of agents matching the specified tier
    """
    return {
        agent_id: data
        for agent_id, data in SAMPLE_AGENTS.items()
        if data["expected_tier"] == tier
    }


def create_custom_agent(
    address: str,
    tx_success: int,
    x402_profitability: int,
    erc8004_stability: int,
    description: str = "Custom test agent",
) -> AgentData:
    """Create a custom agent for testing.

    Args:
        address: Ethereum address
        tx_success: Transaction success score (0-100)
        x402_profitability: Profitability score (0-100)
        erc8004_stability: Stability score (0-100)
        description: Agent description

    Returns:
        Agent data dictionary
    """
    # Calculate expected tier based on scores
    overall = int(
        (tx_success * 0.40 + x402_profitability * 0.40 + erc8004_stability * 0.20) * 10
    )

    if overall >= 850:
        expected_tier = "EXCELLENT"
    elif overall >= 750:
        expected_tier = "GOOD"
    elif overall >= 650:
        expected_tier = "AVERAGE"
    elif overall >= 550:
        expected_tier = "BELOW_AVERAGE"
    else:
        expected_tier = "POOR"

    return {
        "address": address,
        "description": description,
        "expected_tier": expected_tier,
        "mock_scores": {
            "tx_success": tx_success,
            "x402_profitability": x402_profitability,
            "erc8004_stability": erc8004_stability,
        },
    }
