import type { M3ScoredAgentsData, M3AgentScore } from '../types/score';

// M3 Real Agent Scores - from /data/agents/scored-agents.json
// Scored at: 2026-01-29T08:50:30.997836+00:00
// Scoring Version: 1.0.0
// Formula: overall = (txSuccess × 0.40 + x402Profitability × 0.40 + erc8004Stability × 0.20) × 10

export const M3_SCORED_DATA: M3ScoredAgentsData = {
  scored_at: "2026-01-29T08:50:30.997836+00:00",
  scoring_version: "1.0.0",
  formula: "overall = (txSuccess × 0.40 + x402Profitability × 0.40 + erc8004Stability × 0.20) × 10",
  source: {
    file: "real-agents.json",
    collected_at: "2026-01-29T08:47:19.479184Z",
    chains: ["ethereum_sepolia", "base_sepolia"]
  },
  total_scored: 7,
  distribution: {
    average: 721,
    min: 502,
    max: 812,
    median: 812,
    std_dev: 121.13,
    tiers: {
      excellent: 4,
      good: 1,
      average: 2,
      below_average: 0,
      poor: 0
    }
  },
  agents: [
    {
      address: "0x34d6a7e5f9cd22e9b90d3028457c82e1748f344d",
      chain: "base-sepolia",
      chain_id: 84532,
      token_id: 5,
      name: "Jeff Zyfai Agent",
      overall: 812,
      tx_success: 84,
      x402_profitability: 69,
      erc8004_stability: 100,
      risk_level: "low",
      confidence: 60,
      tier: "excellent",
      metadata: {
        x402_support: true,
        services_count: 5,
        active: true,
        description: "Non-custodial deposit funnel into your Zyfai Safe on Base. Backend handles Safe deployment and Zyfai"
      }
    },
    {
      address: "0x34d6a7e5f9cd22e9b90d3028457c82e1748f344d",
      chain: "base-sepolia",
      chain_id: 84532,
      token_id: 4,
      name: "Jeff Zyfai Agent",
      overall: 812,
      tx_success: 84,
      x402_profitability: 69,
      erc8004_stability: 100,
      risk_level: "low",
      confidence: 60,
      tier: "excellent",
      metadata: {
        x402_support: true,
        services_count: 5,
        active: true,
        description: "Non-custodial deposit funnel into your Zyfai Safe on Base. Backend handles Safe deployment and Zyfai"
      }
    },
    {
      address: "0x34d6a7e5f9cd22e9b90d3028457c82e1748f344d",
      chain: "base-sepolia",
      chain_id: 84532,
      token_id: 3,
      name: "Jeff Zyfai Agent",
      overall: 812,
      tx_success: 84,
      x402_profitability: 69,
      erc8004_stability: 100,
      risk_level: "low",
      confidence: 60,
      tier: "excellent",
      metadata: {
        x402_support: true,
        services_count: 5,
        active: true,
        description: "Non-custodial deposit funnel into your Zyfai Safe on Base. Backend handles Safe deployment and Zyfai"
      }
    },
    {
      address: "0x34d6a7e5f9cd22e9b90d3028457c82e1748f344d",
      chain: "base-sepolia",
      chain_id: 84532,
      token_id: 2,
      name: "Jeff Zyfai Agent",
      overall: 812,
      tx_success: 84,
      x402_profitability: 69,
      erc8004_stability: 100,
      risk_level: "low",
      confidence: 60,
      tier: "excellent",
      metadata: {
        x402_support: true,
        services_count: 5,
        active: true,
        description: "Non-custodial deposit funnel into your Zyfai Safe on Base. Backend handles Safe deployment and Zyfai"
      }
    },
    {
      address: "0x81fd234f63dd559d0eda56d17bb1bb78f236db37",
      chain: "sepolia",
      chain_id: 11155111,
      token_id: 2,
      name: "unabotter",
      overall: 724,
      tx_success: 91,
      x402_profitability: 50,
      erc8004_stability: 80,
      risk_level: "medium",
      confidence: 41,
      tier: "good",
      metadata: {
        x402_support: false,
        services_count: 3,
        active: true,
        description: "Autonomous Ethereum developer agent. Builds smart contracts, DeFi tools, trading automation. Sardoni"
      }
    },
    {
      address: "0xa7d83f004caa9ba2f4359edd78a254032e4374ad",
      chain: "base-sepolia",
      chain_id: 84532,
      token_id: 1,
      name: "Agent #1",
      overall: 574,
      tx_success: 76,
      x402_profitability: 50,
      erc8004_stability: 35,
      risk_level: "high",
      confidence: 35,
      tier: "average",
      metadata: {
        x402_support: false,
        services_count: 0,
        active: true,
        description: null
      }
    },
    {
      address: "0x9b4cef62a0ce1671ccfefa6a6d8cbfa165c49831",
      chain: "sepolia",
      chain_id: 11155111,
      token_id: 1,
      name: "Agent #1",
      overall: 502,
      tx_success: 58,
      x402_profitability: 50,
      erc8004_stability: 35,
      risk_level: "high",
      confidence: 32,
      tier: "average",
      metadata: {
        x402_support: false,
        services_count: 0,
        active: true,
        description: null
      }
    }
  ]
};

// Get unique agents (deduplicated by address+chain)
export function getUniqueM3Agents(): M3AgentScore[] {
  const uniqueMap = new Map<string, M3AgentScore>();
  
  for (const agent of M3_SCORED_DATA.agents) {
    const key = `${agent.address}-${agent.chain}`;
    // Keep the one with highest token_id (most recent)
    const existing = uniqueMap.get(key);
    if (!existing || agent.token_id > existing.token_id) {
      uniqueMap.set(key, agent);
    }
  }
  
  return Array.from(uniqueMap.values()).sort((a, b) => b.overall - a.overall);
}

// Export unique agents for display
export const M3_UNIQUE_AGENTS = getUniqueM3Agents();
