interface RiskBreakdownProps {
  subScores: Record<string, number>
}

const moduleLabels: Record<string, string> = {
  behavior_analyzer: 'Behavior',
  velocity_detector: 'Velocity',
  device_risk: 'Device',
  merchant_risk: 'Merchant',
  geolocation: 'Geolocation',
  ip_intelligence: 'IP Intel',
}

export function RiskBreakdown({ subScores }: RiskBreakdownProps) {
  return (
    <div className="space-y-2">
      {Object.entries(subScores).map(([module, score]) => (
        <div key={module} className="flex items-center gap-2">
          <span className="text-xs text-gray-500 w-20 truncate">
            {moduleLabels[module] || module}
          </span>
          <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                score > 60 ? 'bg-red-500' : score > 30 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${score}%` }}
            />
          </div>
          <span className="text-xs font-mono w-8 text-right">{score.toFixed(1)}</span>
        </div>
      ))}
    </div>
  )
}
