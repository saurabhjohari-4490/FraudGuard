import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'

interface RiskDistributionProps {
  data?: { bucket: string; count: number }[]
}

// Color coding by risk zone
function getBarColor(bucket: string): string {
  const low = parseInt(bucket.split('-')[0])
  if (low >= 80) return '#dc2626'   // red - CRITICAL
  if (low >= 60) return '#ea580c'   // orange - ESCALATE
  if (low >= 30) return '#ca8a04'   // yellow - VERIFY
  return '#16a34a'                   // green - APPROVE
}

function getZoneLabel(bucket: string): string {
  const low = parseInt(bucket.split('-')[0])
  if (low >= 80) return 'CRITICAL'
  if (low >= 60) return 'ESCALATE'
  if (low >= 30) return 'VERIFY'
  return 'APPROVE'
}

export function RiskDistribution({ data }: RiskDistributionProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Risk Score Distribution</h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          No data available
        </div>
      </div>
    )
  }

  // Split into safe zone (0-30) and risk zone (30+)
  const safeZone = data.filter((d) => parseInt(d.bucket.split('-')[0]) < 30)
  const riskZone = data.filter((d) => parseInt(d.bucket.split('-')[0]) >= 30)
  const totalSafe = safeZone.reduce((sum, d) => sum + d.count, 0)
  const totalRisk = riskZone.reduce((sum, d) => sum + d.count, 0)

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null
    const item = payload[0].payload
    return (
      <div className="bg-gray-900 text-white px-3 py-2 rounded-lg text-sm shadow-lg">
        <p className="font-medium">Score: {item.bucket}</p>
        <p>Count: {item.count.toLocaleString()}</p>
        <p className="text-xs text-gray-300 mt-1">Zone: {getZoneLabel(item.bucket)}</p>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Risk Score Distribution</h3>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-green-600"></span> Approve
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-yellow-600"></span> Verify
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-orange-600"></span> Escalate
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm bg-red-600"></span> Critical
          </span>
        </div>
      </div>

      {/* Main chart with log scale to show small counts */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="bucket" fontSize={11} tick={{ fill: '#6b7280' }} />
          <YAxis
            fontSize={11}
            tick={{ fill: '#6b7280' }}
            scale="log"
            domain={[0.5, 'auto']}
            allowDataOverflow
            tickFormatter={(val) => val >= 1000 ? `${(val/1000).toFixed(0)}k` : val}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x="30-40" stroke="#ca8a04" strokeDasharray="3 3" label="" />
          <ReferenceLine x="60-70" stroke="#ea580c" strokeDasharray="3 3" label="" />
          <ReferenceLine x="80-90" stroke="#dc2626" strokeDasharray="3 3" label="" />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={getBarColor(entry.bucket)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Risk zone summary cards */}
      <div className="grid grid-cols-4 gap-2 mt-4 pt-4 border-t">
        <div className="text-center p-2 bg-green-50 rounded">
          <p className="text-lg font-bold text-green-700">{totalSafe.toLocaleString()}</p>
          <p className="text-xs text-green-600">Approved (0-30)</p>
        </div>
        <div className="text-center p-2 bg-yellow-50 rounded">
          <p className="text-lg font-bold text-yellow-700">
            {data.filter(d => { const l = parseInt(d.bucket); return l >= 30 && l < 60 }).reduce((s, d) => s + d.count, 0).toLocaleString()}
          </p>
          <p className="text-xs text-yellow-600">Verify (30-60)</p>
        </div>
        <div className="text-center p-2 bg-orange-50 rounded">
          <p className="text-lg font-bold text-orange-700">
            {data.filter(d => { const l = parseInt(d.bucket); return l >= 60 && l < 80 }).reduce((s, d) => s + d.count, 0).toLocaleString()}
          </p>
          <p className="text-xs text-orange-600">Escalate (60-80)</p>
        </div>
        <div className="text-center p-2 bg-red-50 rounded">
          <p className="text-lg font-bold text-red-700">
            {data.filter(d => { const l = parseInt(d.bucket); return l >= 80 }).reduce((s, d) => s + d.count, 0).toLocaleString()}
          </p>
          <p className="text-xs text-red-600">Critical (80-100)</p>
        </div>
      </div>

      {/* Risk highlight callout */}
      {totalRisk > 0 && (
        <div className="mt-3 px-3 py-2 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <span className="text-sm text-red-700">
            <span className="font-semibold">{totalRisk}</span> transactions flagged ({((totalRisk / (totalSafe + totalRisk)) * 100).toFixed(2)}% of total)
          </span>
          <span className="text-xs text-red-500 font-medium">
            {riskZone.filter(d => parseInt(d.bucket) >= 80).reduce((s, d) => s + d.count, 0)} critical
          </span>
        </div>
      )}
    </div>
  )
}
