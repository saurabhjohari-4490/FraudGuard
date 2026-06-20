import { useState, useEffect, useRef } from 'react'
import { api } from '../../api/client'
import { MetricTransaction } from '../../types'

interface TransactionDrillDownProps {
  category: string
  title: string
}

function getRiskColor(score: number): string {
  if (score > 80) return 'text-red-600'
  if (score > 60) return 'text-orange-600'
  if (score > 30) return 'text-yellow-600'
  return 'text-green-600'
}

function getRiskBg(score: number): string {
  if (score > 80) return 'bg-red-50 border-red-200'
  if (score > 60) return 'bg-orange-50 border-orange-200'
  if (score > 30) return 'bg-yellow-50 border-yellow-200'
  return 'bg-green-50 border-green-200'
}

function getRiskLevelBadge(score: number, decision: string, analystAction?: string) {
  if (analystAction === 'block') return { style: 'bg-red-700 text-white ring-2 ring-red-300', label: 'BLOCKED BY ANALYST' }
  if (analystAction === 'approve') return { style: 'bg-green-200 text-green-800', label: 'APPROVED BY ANALYST' }
  if (analystAction === 'escalate') return { style: 'bg-orange-200 text-orange-800', label: 'ESCALATED BY ANALYST' }
  if (score > 80) return { style: 'bg-red-600 text-white', label: 'CRITICAL RISK' }
  if (decision === 'escalate') return { style: 'bg-orange-100 text-orange-700', label: 'ESCALATED' }
  if (decision === 'verify') return { style: 'bg-yellow-100 text-yellow-700', label: 'VERIFY' }
  return { style: 'bg-green-100 text-green-700', label: 'APPROVED' }
}

const moduleLabels: Record<string, string> = {
  behavior_analyzer: 'Behavior',
  velocity_detector: 'Velocity',
  device_risk: 'Device',
  merchant_risk: 'Merchant',
  geolocation: 'Geolocation',
  ip_intelligence: 'IP Intel',
}

function getScoreBarColor(score: number): string {
  if (score >= 70) return 'bg-red-500'
  if (score >= 40) return 'bg-orange-500'
  if (score >= 20) return 'bg-yellow-500'
  return 'bg-green-500'
}

export function TransactionDrillDown({ category, title }: TransactionDrillDownProps) {
  const [transactions, setTransactions] = useState<MetricTransaction[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<MetricTransaction | null>(null)
  const detailPanelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (selected && detailPanelRef.current && !detailPanelRef.current.contains(event.target as Node)) {
        setSelected(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [selected])

  useEffect(() => {
    async function fetch() {
      try {
        const res = await api.get('/api/v1/metrics/transactions', { params: { category } })
        setTransactions(res.data.transactions)
      } catch {
        setTransactions([])
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [category])

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse h-16 bg-gray-200 rounded-lg" />
        ))}
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No transactions found for "{title}"
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Transaction List */}
      <div className={selected ? 'lg:col-span-1' : 'lg:col-span-3'}>
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="px-4 py-3 border-b bg-gray-50">
            <h3 className="font-semibold text-gray-900">{title}</h3>
            <p className="text-xs text-gray-500 mt-0.5">{transactions.length} transactions</p>
          </div>
          <div className="divide-y max-h-[calc(100vh-250px)] overflow-y-auto">
            {transactions.map((txn) => (
              <div
                key={txn.transaction_id}
                onClick={() => setSelected(txn)}
                className={`p-4 cursor-pointer transition-colors ${
                  selected?.transaction_id === txn.transaction_id
                    ? 'bg-blue-50 border-l-4 border-l-blue-500'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {(() => {
                      const badge = getRiskLevelBadge(txn.risk_score, txn.decision, txn.analyst_action)
                      return (
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${badge.style}`}>
                          {badge.label}
                        </span>
                      )
                    })()}
                    <span className="font-mono text-xs text-gray-600">{txn.transaction_id}</span>
                  </div>
                  <span className={`text-lg font-bold ${getRiskColor(txn.risk_score)}`}>
                    {txn.risk_score.toFixed(1)}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-1.5 text-xs text-gray-500">
                  <span>User: {txn.user_id}</span>
                  <span>{txn.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detail Panel */}
      {selected && (
        <div className="lg:col-span-2" ref={detailPanelRef}>
          <div className="bg-white rounded-xl border shadow-lg overflow-hidden sticky top-6">
            {/* Header */}
            <div className="bg-gray-900 text-white px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400 uppercase tracking-wider">Transaction Detail</p>
                  <p className="font-mono text-sm mt-1">{selected.transaction_id}</p>
                </div>
                <button
                  onClick={() => setSelected(null)}
                  className="text-gray-400 hover:text-white text-xl leading-none"
                >
                  &times;
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6 max-h-[calc(100vh-250px)] overflow-y-auto">
              {/* Risk Score */}
              <div className="text-center py-3">
                <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full border-4 ${getRiskBg(selected.risk_score)}`}>
                  <span className={`text-2xl font-bold ${getRiskColor(selected.risk_score)}`}>
                    {selected.risk_score.toFixed(1)}
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-500">Risk Score / 100</p>
                {(() => {
                  const badge = getRiskLevelBadge(selected.risk_score, selected.decision, selected.analyst_action)
                  return (
                    <div className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-bold ${badge.style}`}>
                      {badge.label}
                    </div>
                  )
                })()}
              </div>

              {/* Transaction Info */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs uppercase">Amount</p>
                  <p className="font-semibold text-gray-900 mt-0.5">
                    {selected.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs uppercase">User</p>
                  <p className="font-mono font-semibold text-gray-900 mt-0.5">{selected.user_id}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs uppercase">Merchant</p>
                  <p className="font-mono font-semibold text-gray-900 mt-0.5">{selected.merchant_id}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-gray-500 text-xs uppercase">Time</p>
                  <p className="font-semibold text-gray-900 mt-0.5">
                    {selected.decided_at ? new Date(selected.decided_at).toLocaleString() : '-'}
                  </p>
                </div>
              </div>

              {/* Module Score Breakdown */}
              {selected.sub_scores && Object.keys(selected.sub_scores).length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Risk Score Breakdown</h3>
                  <div className="space-y-2">
                    {Object.entries(selected.sub_scores)
                      .sort(([, a], [, b]) => b - a)
                      .map(([module, score]) => (
                        <div key={module} className="bg-gray-50 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-gray-700">
                              {moduleLabels[module] || module}
                            </span>
                            <span className={`text-sm font-bold ${getRiskColor(score)}`}>
                              {score.toFixed(1)}/100
                            </span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${getScoreBarColor(score)}`}
                              style={{ width: `${score}%` }}
                            />
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Signals */}
              {selected.signals && selected.signals.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">
                    Fraud Signals ({selected.signals.length})
                  </h3>
                  <div className="space-y-1.5">
                    {selected.signals.map((signal, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                        <span className="text-red-500 flex-shrink-0">&#x26A0;</span>
                        <span className="text-gray-700">{signal}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Explanation */}
              {selected.explanation && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">AI Explanation</h3>
                  <p className="text-sm text-gray-600 bg-blue-50 border border-blue-100 rounded-lg p-3">
                    {selected.explanation}
                  </p>
                </div>
              )}

              {/* Analyst Actions — show when no action taken yet */}
              {!selected.analyst_action && (selected.decision === 'escalate' || selected.decision === 'verify') && (
                <div className="border-t pt-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Analyst Actions</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={async () => {
                        await api.patch(`/api/v1/alerts/${selected.id}`, { analyst_action: 'approve' })
                        setSelected({ ...selected, analyst_action: 'approve' })
                        setTransactions((prev) => prev.map((t) =>
                          t.transaction_id === selected.transaction_id ? { ...t, analyst_action: 'approve' } : t
                        ))
                      }}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                    >
                      Approve
                    </button>
                    {selected.decision === 'verify' && (
                      <button
                        onClick={async () => {
                          await api.patch(`/api/v1/alerts/${selected.id}`, { analyst_action: 'escalate' })
                          setSelected({ ...selected, analyst_action: 'escalate' })
                          setTransactions((prev) => prev.map((t) =>
                            t.transaction_id === selected.transaction_id ? { ...t, analyst_action: 'escalate' } : t
                          ))
                        }}
                        className="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors"
                      >
                        Escalate
                      </button>
                    )}
                    <button
                      onClick={async () => {
                        await api.patch(`/api/v1/alerts/${selected.id}`, { analyst_action: 'block' })
                        setSelected({ ...selected, analyst_action: 'block' })
                        setTransactions((prev) => prev.map((t) =>
                          t.transaction_id === selected.transaction_id ? { ...t, analyst_action: 'block' } : t
                        ))
                      }}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
                    >
                      Block
                    </button>
                  </div>
                </div>
              )}

              {/* Analyst Status (for resolved actions) */}
              {selected.analyst_action && (
                <div className="border-t pt-4">
                  {(() => {
                    const statusBadge = getRiskLevelBadge(selected.risk_score, selected.decision, selected.analyst_action)
                    return (
                      <div className={`rounded-lg p-4 text-center ${
                        selected.analyst_action === 'block' ? 'bg-red-50 border border-red-200' :
                        selected.analyst_action === 'approve' ? 'bg-green-50 border border-green-200' :
                        'bg-orange-50 border border-orange-200'
                      }`}>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${statusBadge.style}`}>
                          {statusBadge.label}
                        </span>
                      </div>
                    )
                  })()}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
