interface SampleAgentsProps {
  onSelect: (address: string) => void;
}

const SAMPLE_AGENTS = [
  { 
    name: 'Excellent Trader', 
    address: '0x1111111111111111111111111111111111111111', 
    tier: 'excellent',
    color: 'bg-green-100 text-green-700 hover:bg-green-200'
  },
  { 
    name: 'Good Analyst', 
    address: '0x2222222222222222222222222222222222222222', 
    tier: 'good',
    color: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
  },
  { 
    name: 'Average Bot', 
    address: '0x3333333333333333333333333333333333333333', 
    tier: 'average',
    color: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
  },
  { 
    name: 'Struggling Agent', 
    address: '0x4444444444444444444444444444444444444444', 
    tier: 'below_average',
    color: 'bg-orange-100 text-orange-700 hover:bg-orange-200'
  },
  { 
    name: 'Risky Agent', 
    address: '0x5555555555555555555555555555555555555555', 
    tier: 'poor',
    color: 'bg-red-100 text-red-700 hover:bg-red-200'
  },
];

export function SampleAgents({ onSelect }: SampleAgentsProps) {
  return (
    <div className="mt-8">
      <h3 className="text-center text-gray-600 mb-4">Or try a sample agent:</h3>
      <div className="flex flex-wrap justify-center gap-2">
        {SAMPLE_AGENTS.map((agent) => (
          <button
            key={agent.address}
            onClick={() => onSelect(agent.address)}
            className={`px-4 py-2 rounded-full font-medium transition-colors ${agent.color}`}
          >
            {agent.name}
          </button>
        ))}
      </div>
    </div>
  );
}
