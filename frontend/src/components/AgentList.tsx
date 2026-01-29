import { useState } from 'react';
import { ExternalLink, Star, MessageSquare, Zap } from 'lucide-react';
import type { Agent8004 } from '../types/agent';
import { CHAIN_COLORS } from '../types/agent';

interface AgentListProps {
  agents: Agent8004[];
  onSelectAgent: (address: string) => void;
}

function shortenAddress(address: string): string {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

function getScoreColor(score: number): string {
  if (score >= 85) return 'text-green-600';
  if (score >= 75) return 'text-blue-600';
  if (score >= 65) return 'text-yellow-600';
  if (score >= 55) return 'text-orange-600';
  return 'text-red-600';
}

export function AgentList({ agents, onSelectAgent }: AgentListProps) {
  const [view, setView] = useState<'grid' | 'table'>('grid');

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          ERC-8004 Agent Registry
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setView('grid')}
            className={`px-3 py-1 rounded ${view === 'grid' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'}`}
          >
            Grid
          </button>
          <button
            onClick={() => setView('table')}
            className={`px-3 py-1 rounded ${view === 'table' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-600'}`}
          >
            Table
          </button>
        </div>
      </div>

      {view === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div
              key={`${agent.chain}-${agent.id}`}
              onClick={() => onSelectAgent(agent.address)}
              className="bg-white rounded-xl shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer border border-gray-100"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  {agent.avatar ? (
                    <img
                      src={agent.avatar}
                      alt={agent.name}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold">
                      {agent.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div>
                    <h3 className="font-semibold text-gray-800">{agent.name}</h3>
                    <p className="text-xs text-gray-500 font-mono">
                      {shortenAddress(agent.address)}
                    </p>
                  </div>
                </div>
                <span className={`text-2xl font-bold ${getScoreColor(agent.score)}`}>
                  {agent.score > 0 ? agent.score.toFixed(0) : '-'}
                </span>
              </div>

              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className={`text-xs px-2 py-1 rounded-full ${CHAIN_COLORS[agent.chain] || 'bg-gray-100 text-gray-600'}`}>
                  {agent.chain}
                </span>
                <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                  {agent.endpoint}
                </span>
                {agent.hasX402 && (
                  <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 flex items-center gap-1">
                    <Zap className="w-3 h-3" /> X402
                  </span>
                )}
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Star className="w-3 h-3" /> {agent.stars}
                  </span>
                  <span className="flex items-center gap-1">
                    <MessageSquare className="w-3 h-3" /> {agent.feedback}
                  </span>
                </div>
                <span>{agent.createdAt}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Name</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Chain</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Score</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Endpoint</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">X402</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {agents.map((agent) => (
                <tr
                  key={`${agent.chain}-${agent.id}`}
                  onClick={() => onSelectAgent(agent.address)}
                  className="hover:bg-gray-50 cursor-pointer"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {agent.avatar ? (
                        <img src={agent.avatar} alt="" className="w-8 h-8 rounded-full" />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                          {agent.name.charAt(0)}
                        </div>
                      )}
                      <div>
                        <div className="font-medium text-gray-800">{agent.name}</div>
                        <div className="text-xs text-gray-500 font-mono">{shortenAddress(agent.address)}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${CHAIN_COLORS[agent.chain] || 'bg-gray-100'}`}>
                      {agent.chain}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-bold ${getScoreColor(agent.score)}`}>
                      {agent.score > 0 ? agent.score.toFixed(1) : '-'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{agent.endpoint}</td>
                  <td className="px-4 py-3">
                    {agent.hasX402 && (
                      <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                        X402
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{agent.createdAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-4 text-center">
        <a
          href="https://www.8004scan.io/agents"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-sm"
        >
          View all agents on 8004scan <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}
