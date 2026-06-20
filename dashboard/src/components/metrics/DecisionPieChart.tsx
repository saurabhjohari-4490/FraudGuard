interface DecisionPieChartProps {
  decisions?: Record<string, number>
}

const COLORS: Record<string, string> = {
  approve: '#22c55e',
  verify: '#eab308',
  escalate: '#f97316',
  block: '#ef4444',
}

const LABELS: Record<string, string> = {
  approve: 'Approved',
  verify: 'Verification Pending',
  escalate: 'Escalated',
  block: 'Blocked (by analyst)',
}

const ORDER = ['approve', 'verify', 'escalate', 'block']

export function DecisionPieChart({ decisions }: DecisionPieChartProps) {
  if (!decisions || Object.keys(decisions).length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Decision Distribution</h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          No data available
        </div>
      </div>
    )
  }

  const total = Object.values(decisions).reduce((sum, v) => sum + v, 0)
  const maxCount = Math.max(...Object.values(decisions), 1)

  const data = ORDER
    .filter((key) => decisions[key] !== undefined)
    .map((key) => ({
      key,
      label: LABELS[key] || key,
      value: decisions[key] || 0,
      color: COLORS[key] || '#6b7280',
      percent: total > 0 ? ((decisions[key] || 0) / total) * 100 : 0,
      barWidth: ((decisions[key] || 0) / maxCount) * 100,
    }))

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="font-semibold mb-4">Decision Distribution</h3>
      <div className="space-y-4">
        {data.map((entry) => (
          <div key={entry.key}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-sm font-medium text-gray-700">{entry.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-gray-900">
                  {entry.value.toLocaleString()}
                </span>
                <span className="text-xs text-gray-400 w-16 text-right">
                  {entry.percent >= 1
                    ? `${entry.percent.toFixed(1)}%`
                    : entry.percent > 0
                      ? `${entry.percent.toFixed(2)}%`
                      : '0%'}
                </span>
              </div>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2.5">
              <div
                className="h-2.5 rounded-full transition-all duration-500"
                style={{
                  width: `${Math.max(entry.barWidth, 1)}%`,
                  backgroundColor: entry.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 pt-3 border-t border-gray-100 flex justify-between text-xs text-gray-400">
        <span>Total: {total.toLocaleString()} transactions</span>
        <span>{data.length} decision types</span>
      </div>
    </div>
  )
}
