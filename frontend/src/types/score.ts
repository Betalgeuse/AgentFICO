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
