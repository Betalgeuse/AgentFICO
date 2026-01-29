import { useState } from 'react';
import { Zap, Shield, AlertTriangle, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import type { M3AgentScore } from '../types/score';
import { RISK_TEXT_COLORS } from '../types/score';
import { CHAIN_COLORS } from '../types/agent';
import { M3_UNIQUE_AGENTS, M3_SCORED_DATA } from '../data/realAgents';

interface RealAgentListProps {
  onSelectAgent: (agent: M3AgentScore) => void;
}

function shortenAddress(address: string): string {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

function getTierColor(tier: string): string {
  const colors: Record<string, string> = {
    excellent: 'text-green-600 bg-green-50',
    good: 'text-blue-600 bg-blue-50',
    average: 'text-yellow-600 bg-yellow-50',
    below_average: 'text-orange-600 bg-orange-50',
    poor: 'text-red-600 bg-red-50',
  };
  return colors[tier] || 'text-gray-600 bg-gray-50';
}

function getRiskIcon(risk: string) {
  switch (risk) {
    case 'low':
      return <Shield className="w-4 h-4 text-green-500" />;
    case 'medium':
      return <TrendingUp className="w-4 h-4 text-yellow-500" />;
    case 'high':
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    default:
      return null;
  }
}

export function RealAgentList({ onSelectAgent }: RealAgentListProps) {
  const [selectedAgent, setSelectedAgent] = useState<M3AgentScore | null>(null);
  const [showAll, setShowAll] = useState(false);
  
  const displayAgents = showAll ? M3_UNIQUE_AGENTS : M3_UNIQUE_AGENTS.slice(0, 4);

  const handleSelect = (agent: M3AgentScore) => {
    if (selectedAgent?.address === agent.address && selectedAgent?.chain === agent.chain) {
      setSelectedAgent(null);
    } else {
      setSelectedAgent(agent);
      onSelectAgent(agent);
    }
  };

  return (
    <div className="mt-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-gray-800">
              Real ERC-8004 Agents (M3)
            </h2>
            <span className="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded-full">
              LIVE DATA
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {M3_SCORED_DATA.total_scored} scored agents • Avg: {M3_SCORED_DATA.distribution.average} • 
            Range: {M3_SCORED_DATA.distribution.min}-{M3_SCORED_DATA.distribution.max}
          </p>
        </div>
        <div className="text-right text-xs text-gray-400">
          <p>Scoring v{M3_SCORED_DATA.scoring_version}</p>
          <p>Scored: {new Date(M3_SCORED_DATA.scored_at).toLocaleDateString()}</p>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 mb-4">
        <div className="grid grid-cols-5 gap-4 text-center">
          {Object.entries(M3_SCORED_DATA.distribution.tiers).map(([tier, count]) => (
            <div key={tier} className="text-center">
              <div className={`text-lg font-bold ${RISK_TEXT_COLORS[tier] || 'text-gray-700'}`}>
                {count}
              </div>
              <div className="text-xs text-gray-500 capitalize">
                {tier.replace('_', ' ')}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {displayAgents.map((agent) => (
          <div
            key={`${agent.chain}-${agent.token_id}`}
            onClick={() => handleSelect(agent)}
            className={`bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition-all cursor-pointer border-2 ${
              selectedAgent?.address === agent.address && selectedAgent?.chain === agent.chain
                ? 'border-indigo-500 ring-2 ring-indigo-200'
                : 'border-transparent'
            }`}
          >
            {/* Header Row */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                  {agent.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">{agent.name}</h3>
                  <p className="text-xs text-gray-500 font-mono">
                    {shortenAddress(agent.address)}
                  </p>
                </div>
              </div>
              
              {/* Score Badge */}
              <div className="text-right">
                <div className={`text-3xl font-bold ${RISK_TEXT_COLORS[agent.tier]}`}>
                  {agent.overall}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getTierColor(agent.tier)}`}>
                  {agent.tier.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Tags Row */}
            <div className="mt-3 flex items-center gap-2 flex-wrap">
              <span className={`text-xs px-2 py-1 rounded-full ${CHAIN_COLORS[agent.chain] || 'bg-gray-100 text-gray-600'}`}>
                {agent.chain}
              </span>
              <span className={`text-xs px-2 py-1 rounded-full flex items-center gap-1 ${
                agent.risk_level === 'low' ? 'bg-green-100 text-green-700' :
                agent.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {getRiskIcon(agent.risk_level)}
                {agent.risk_level} risk
              </span>
              {agent.metadata.x402_support && (
                <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700 flex items-center gap-1">
                  <Zap className="w-3 h-3" /> X402
                </span>
              )}
              <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                Token #{agent.token_id}
              </span>
            </div>

            {/* Score Breakdown (Expanded) */}
            {selectedAgent?.address === agent.address && selectedAgent?.chain === agent.chain && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <h4 className="text-sm font-semibold text-gray-600 mb-3">Score Breakdown</h4>
                <div className="space-y-2">
                  <BreakdownBar 
                    label="TX Success" 
                    value={agent.tx_success} 
                    weight="40%" 
                    color="bg-indigo-500" 
                  />
                  <BreakdownBar 
                    label="x402 Profit" 
                    value={agent.x402_profitability} 
                    weight="40%" 
                    color="bg-purple-500" 
                  />
                  <BreakdownBar 
                    label="ERC-8004 Stability" 
                    value={agent.erc8004_stability} 
                    weight="20%" 
                    color="bg-violet-500" 
                  />
                </div>
                
                <div className="mt-3 flex justify-between text-xs text-gray-500">
                  <span>Confidence: <strong className="text-gray-700">{agent.confidence}%</strong></span>
                  <span>Services: {agent.metadata.services_count}</span>
                </div>
                
                {agent.metadata.description && (
                  <p className="mt-3 text-xs text-gray-500 italic">
                    "{agent.metadata.description}"
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Show More/Less */}
      {M3_UNIQUE_AGENTS.length > 4 && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="mt-4 w-full py-2 text-sm text-indigo-600 hover:text-indigo-800 flex items-center justify-center gap-1"
        >
          {showAll ? (
            <>Show Less <ChevronUp className="w-4 h-4" /></>
          ) : (
            <>Show All {M3_UNIQUE_AGENTS.length} Agents <ChevronDown className="w-4 h-4" /></>
          )}
        </button>
      )}

      {/* Formula Info */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500">
        <strong>Scoring Formula:</strong> {M3_SCORED_DATA.formula}
      </div>
    </div>
  );
}

// Breakdown Bar Component
function BreakdownBar({ 
  label, 
  value, 
  weight, 
  color 
}: { 
  label: string; 
  value: number; 
  weight: string; 
  color: string; 
}) {
  return (
    <div className="flex items-center">
      <div className="w-28 text-xs text-gray-600">
        {label}
        <span className="text-gray-400 ml-1">({weight})</span>
      </div>
      <div className="flex-1 mx-2">
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${color}`}
            style={{ width: `${value}%` }}
          />
        </div>
      </div>
      <div className="w-10 text-right text-xs font-semibold text-gray-700">
        {value}
      </div>
    </div>
  );
}
