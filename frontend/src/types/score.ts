export interface AgentScore {
  agentAddress: string;
  overall: number;
  txSuccess: number;
  x402Profitability: number;
  erc8004Stability: number;
  riskLevel: number;
  riskLevelName: string;
  confidence: number;
  timestamp: string;
  breakdown?: {
    weights: Record<string, number>;
    sources: Record<string, unknown>;
  };
}

// M3 Real Agent Score (from scored-agents.json)
export interface M3AgentScore {
  address: string;
  chain: string;
  chain_id: number;
  token_id: number;
  name: string;
  overall: number;
  tx_success: number;
  x402_profitability: number;
  erc8004_stability: number;
  risk_level: 'low' | 'medium' | 'high';
  confidence: number;
  tier: RiskTier;
  metadata: {
    x402_support: boolean;
    services_count: number;
    active: boolean;
    description: string | null;
  };
}

export interface M3ScoredAgentsData {
  scored_at: string;
  scoring_version: string;
  formula: string;
  source: {
    file: string;
    collected_at: string;
    chains: string[];
  };
  total_scored: number;
  distribution: {
    average: number;
    min: number;
    max: number;
    median: number;
    std_dev: number;
    tiers: Record<RiskTier, number>;
  };
  agents: M3AgentScore[];
}

export type RiskTier = 'excellent' | 'good' | 'average' | 'below_average' | 'poor';

export const RISK_COLORS: Record<string, string> = {
  excellent: 'bg-green-500',
  good: 'bg-blue-500',
  average: 'bg-yellow-500',
  below_average: 'bg-orange-500',
  poor: 'bg-red-500',
};

export const RISK_TEXT_COLORS: Record<string, string> = {
  excellent: 'text-green-500',
  good: 'text-blue-500',
  average: 'text-yellow-500',
  below_average: 'text-orange-500',
  poor: 'text-red-500',
};
