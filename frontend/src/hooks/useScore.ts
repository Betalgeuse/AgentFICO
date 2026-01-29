import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { AgentScore } from '../types/score';

export function useScore(address: string | null) {
  return useQuery<AgentScore, Error>({
    queryKey: ['score', address],
    queryFn: () => api.getScore(address!),
    enabled: !!address && address.length === 42,
    staleTime: 60 * 1000, // 1 minute
    retry: 1,
  });
}

export function useContractScore(address: string | null) {
  return useQuery<AgentScore, Error>({
    queryKey: ['contractScore', address],
    queryFn: () => api.getContractScore(address!),
    enabled: !!address && address.length === 42,
    staleTime: 60 * 1000,
    retry: 1,
  });
}
