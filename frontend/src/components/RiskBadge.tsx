import { RISK_COLORS } from '../types/score';

interface RiskBadgeProps {
  level: string;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  const normalizedLevel = level.toLowerCase().replace(' ', '_');
  const bgColor = RISK_COLORS[normalizedLevel] || 'bg-gray-500';
  
  return (
    <span className={`${bgColor} text-white text-sm font-semibold px-3 py-1 rounded-full uppercase`}>
      {level.replace('_', ' ')}
    </span>
  );
}
