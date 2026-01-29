export interface Agent8004 {
  id: number;
  name: string;
  address: string;
  chain: string;
  chainIcon: string;
  endpoint: string;
  score: number;
  feedback: number;
  stars: number;
  owner: string;
  hasX402: boolean;
  createdAt: string;
  avatar?: string;
}

export const CHAIN_ICONS: Record<string, string> = {
  'sepolia': '🔷',
  'base-sepolia': '🔵',
  'base': '🔵',
  'ethereum': '⬛',
};

export const CHAIN_COLORS: Record<string, string> = {
  'sepolia': 'bg-blue-100 text-blue-700',
  'base-sepolia': 'bg-indigo-100 text-indigo-700',
  'base': 'bg-indigo-100 text-indigo-700',
  'ethereum': 'bg-gray-100 text-gray-700',
};
