import axios from 'axios';
import type { AgentScore } from '../types/score';
import type { Agent8004 } from '../types/agent';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

export interface AgentListResponse {
  agents: Agent8004[];
  total: number;
  hasMore: boolean;
  chain: string;
}

export interface AgentStatsResponse {
  totalAgents: number;
  byChain: {
    sepolia: number;
    'base-sepolia': number;
  };
  timestamp: string;
}

export const api = {
  getScore: async (address: string): Promise<AgentScore> => {
    const { data } = await client.get(`/v1/score/${address}`);
    return data;
  },

  getContractScore: async (address: string): Promise<AgentScore> => {
    const { data } = await client.get(`/v1/contract/score/${address}`);
    return data;
  },

  getStats: async () => {
    const { data } = await client.get('/v1/contract/stats');
    return data;
  },

  healthCheck: async () => {
    const { data } = await client.get('/health');
    return data;
  },

  // ERC-8004 Agents API
  getAgents: async (params?: {
    chain?: string;
    limit?: number;
    offset?: number;
  }): Promise<AgentListResponse> => {
    const { data } = await client.get('/v1/agents', { params });
    // API 응답을 프론트엔드 타입으로 변환
    return {
      ...data,
      agents: data.agents.map((a: any) => ({
        id: a.agentId,
        name: a.name,
        address: a.agentWallet || a.owner,
        chain: a.chain,
        chainIcon: a.chain === 'sepolia' ? '🔷' : '🔵',
        endpoint: a.services?.[0]?.name || 'CUSTOM',
        score: 0, // 점수는 별도 조회 필요
        feedback: 0,
        stars: 0,
        owner: a.owner,
        hasX402: a.x402Support,
        createdAt: a.fetchedAt,
        avatar: a.image,
      })),
    };
  },

  getAgent: async (agentId: number, chain: string = 'sepolia') => {
    const { data } = await client.get(`/v1/agents/${agentId}`, {
      params: { chain },
    });
    return data;
  },

  getAgentStats: async (): Promise<AgentStatsResponse> => {
    const { data } = await client.get('/v1/agents/stats/summary');
    return data;
  },
};

export default api;
