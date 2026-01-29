interface ScoreBreakdownProps {
  txSuccess: number;
  x402Profitability: number;
  erc8004Stability: number;
}

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7'];

export function ScoreBreakdown({ txSuccess, x402Profitability, erc8004Stability }: ScoreBreakdownProps) {
  const data = [
    { name: 'TX Success', value: txSuccess, weight: '40%', color: '#6366f1' },
    { name: 'x402 Profit', value: x402Profitability, weight: '40%', color: '#8b5cf6' },
    { name: 'ERC-8004', value: erc8004Stability, weight: '20%', color: '#a855f7' },
  ];

  return (
    <div className="w-full">
      <h3 className="text-sm font-semibold text-gray-600 mb-3">Score Breakdown</h3>
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={item.name} className="flex items-center">
            <div className="w-24 text-sm text-gray-600">
              {item.name}
              <span className="text-xs text-gray-400 ml-1">({item.weight})</span>
            </div>
            <div className="flex-1 mx-3">
              <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${item.value}%`, 
                    backgroundColor: COLORS[index] 
                  }}
                />
              </div>
            </div>
            <div className="w-12 text-right text-sm font-semibold" style={{ color: COLORS[index] }}>
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
