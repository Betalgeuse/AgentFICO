import axios from 'axios';
import type { AgentScore } from '../types/score';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

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
};

export default api;
