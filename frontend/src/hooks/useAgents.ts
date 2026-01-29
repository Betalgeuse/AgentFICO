import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { AgentListResponse, AgentStatsResponse } from '../api/client';

export function useAgents(params?: {
  chain?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery<AgentListResponse, Error>({
    queryKey: ['agents', params?.chain, params?.limit, params?.offset],
    queryFn: () => api.getAgents(params),
    staleTime: 60 * 1000, // 1 minute
    retry: 2,
  });
}

export function useAgentStats() {
  return useQuery<AgentStatsResponse, Error>({
    queryKey: ['agentStats'],
    queryFn: () => api.getAgentStats(),
    staleTime: 60 * 1000,
    retry: 2,
  });
}
