interface ScoreGaugeProps {
  value: number;
  max?: number;
  size?: number;
}

function getScoreColor(score: number): string {
  if (score >= 850) return '#22c55e'; // green-500
  if (score >= 750) return '#3b82f6'; // blue-500
  if (score >= 650) return '#eab308'; // yellow-500
  if (score >= 550) return '#f97316'; // orange-500
  return '#ef4444'; // red-500
}

export function ScoreGauge({ value, max = 1000, size = 200 }: ScoreGaugeProps) {
  const percentage = Math.min(value / max, 1);
  const color = getScoreColor(value);
  
  // SVG arc parameters
  const strokeWidth = 20;
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius; // Half circle
  const offset = circumference * (1 - percentage);
  
  return (
    <div className="relative" style={{ width: size, height: size / 2 + 40 }}>
      <svg width={size} height={size / 2 + 20} className="transform -rotate-0">
        {/* Background arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <path
          d={`M ${strokeWidth / 2} ${size / 2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${size / 2}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      
      {/* Score text */}
      <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
        <span className="text-4xl font-bold" style={{ color }}>{value}</span>
        <span className="text-gray-500 text-sm">/ {max}</span>
      </div>
    </div>
  );
}
