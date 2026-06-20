import { RecentTransaction } from '../../types'

interface RecentHighRiskListProps {
  transactions: RecentTransaction[]
  loading: boolean
}

function getRiskColor(score: number): string {
  if (score > 80) return 'text-red-600'
  if (score > 60) return 'text-orange-600'
  if (score > 30) return 'text-yellow-600'
  return 'text-green-600'
}

function getRiskBadge(score: number, decision: string, analystAction?: string) {
  if (analystAction === 'block') return { style: 'bg-red-700 text-white ring-2 ring-red-300', label: 'BLOCKED BY ANALYST' }
  if (score > 80) return { style: 'bg-red-600 text-white', label: 'CRITICAL RISK' }
  if (decision === 'escalate') return { style: 'bg-orange-100 text-orange-700', label: 'ESCALATED' }
  if (decision === 'verify') return { style: 'bg-yellow-100 text-yellow-700', label: 'VERIFY' }
  if (analystAction === 'approve') return { style: 'bg-green-200 text-green-800', label: 'APPROVED BY ANALYST' }
  return { style: 'bg-green-100 text-green-700', label: 'APPROVED' }
}

export function RecentHighRiskList({ transactions, loading }: RecentHighRiskListProps) {
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Recent High-Risk Transactions</h3>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse h-14 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Recent High-Risk Transactions</h3>
        <p className="text-gray-400 text-sm text-center py-8">No high-risk transactions detected</p>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="font-semibold mb-4">Recent High-Risk Transactions</h3>
      <div className="space-y-2 max-h-[350px] overflow-y-auto">
        {transactions.map((txn) => {
          const badge = getRiskBadge(txn.risk_score, txn.decision, txn.analyst_action)
          return (
            <div
              key={txn.transaction_id}
              className={`flex items-center justify-between p-3 rounded-lg hover:shadow-sm transition-all ${
                txn.analyst_action === 'block'
                  ? 'bg-red-100 border-2 border-red-400'
                  : txn.risk_score > 80
                    ? 'bg-red-50 border border-red-200'
                    : 'bg-gray-50 hover:bg-gray-100'
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${badge.style}`}>
                    {badge.label}
                  </span>
                  <span className="font-mono text-xs text-gray-600 truncate">{txn.transaction_id}</span>
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-gray-500">User: {txn.user_id}</span>
                  <span className="text-xs text-gray-500">
                    {txn.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                  </span>
                </div>
                {txn.signals.length > 0 && (
                  <div className="flex gap-1 mt-1 flex-wrap">
                    {txn.signals.slice(0, 2).map((s, i) => (
                      <span key={i} className="text-[10px] bg-red-50 text-red-600 px-1.5 py-0.5 rounded">
                        {s}
                      </span>
                    ))}
                    {txn.signals.length > 2 && (
                      <span className="text-[10px] text-gray-400">+{txn.signals.length - 2}</span>
                    )}
                  </div>
                )}
              </div>
              <div className="text-right ml-3">
                <p className={`text-lg font-bold ${getRiskColor(txn.risk_score)}`}>
                  {txn.risk_score.toFixed(1)}
                </p>
                <p className="text-[10px] text-gray-400">risk score</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
