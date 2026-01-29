import type { AgentScore } from '../types/score';
import { ScoreGauge } from './ScoreGauge';
import { ScoreBreakdown } from './ScoreBreakdown';
import { RiskBadge } from './RiskBadge';

interface ScoreCardProps {
  score: AgentScore;
}

export function ScoreCard({ score }: ScoreCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 max-w-md mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">AgentFICO Score</h2>
        <RiskBadge level={score.riskLevelName} />
      </div>
      
      {/* Address */}
      <div className="text-sm text-gray-500 mb-4 font-mono truncate">
        {score.agentAddress}
      </div>
      
      {/* Gauge */}
      <div className="flex justify-center mb-6">
        <ScoreGauge value={score.overall} max={1000} size={200} />
      </div>
      
      {/* Breakdown */}
      <div className="border-t pt-4">
        <ScoreBreakdown
          txSuccess={score.txSuccess}
          x402Profitability={score.x402Profitability}
          erc8004Stability={score.erc8004Stability}
        />
      </div>
      
      {/* Footer */}
      <div className="mt-4 pt-4 border-t flex justify-between text-sm text-gray-500">
        <span>Confidence: <strong className="text-gray-700">{score.confidence}%</strong></span>
        <span>Updated: {new Date(score.timestamp).toLocaleString()}</span>
      </div>
    </div>
  );
}
