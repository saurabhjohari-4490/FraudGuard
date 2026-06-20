import { useState } from 'react'
import { Alert } from '../../types'

interface AlertDetailPanelProps {
  alert: Alert
  onClose: () => void
  onAction: (alertId: string, action: string, notes?: string) => void
}

const moduleLabels: Record<string, { name: string; description: string }> = {
  behavior_analyzer: { name: 'Behavior Analysis', description: 'Spending patterns vs user history' },
  velocity_detector: { name: 'Velocity Detection', description: 'Transaction frequency & bursts' },
  device_risk: { name: 'Device Risk', description: 'Emulator, rooted, new/shared device' },
  merchant_risk: { name: 'Merchant Risk', description: 'Category risk & fraud association' },
  geolocation: { name: 'Geolocation', description: 'Impossible travel & geo anomalies' },
  ip_intelligence: { name: 'IP Intelligence', description: 'VPN, TOR, proxy, datacenter' },
}

function getScoreColor(score: number): string {
  if (score >= 70) return 'bg-red-500'
  if (score >= 40) return 'bg-orange-500'
  if (score >= 20) return 'bg-yellow-500'
  return 'bg-green-500'
}

function getScoreTextColor(score: number): string {
  if (score >= 70) return 'text-red-600'
  if (score >= 40) return 'text-orange-600'
  if (score >= 20) return 'text-yellow-600'
  return 'text-green-600'
}

function getRiskLevelBadge(score: number, decision: string, analystAction?: string | null) {
  if (analystAction === 'block') return { style: 'bg-red-700 text-white ring-2 ring-red-300', label: 'BLOCKED BY ANALYST' }
  if (analystAction === 'approve') return { style: 'bg-green-200 text-green-800', label: 'APPROVED BY ANALYST' }
  if (analystAction === 'escalate') return { style: 'bg-orange-200 text-orange-800', label: 'ESCALATED BY ANALYST' }
  if (score > 80) return { style: 'bg-red-600 text-white', label: 'CRITICAL RISK' }
  if (decision === 'escalate') return { style: 'bg-orange-100 text-orange-700 border border-orange-300', label: 'ESCALATED' }
  if (decision === 'verify') return { style: 'bg-yellow-100 text-yellow-700 border border-yellow-300', label: 'VERIFY' }
  return { style: 'bg-green-100 text-green-700 border border-green-300', label: 'APPROVED' }
}

function getSignalIcon(signal: string): string {
  if (signal.includes('VPN') || signal.includes('TOR') || signal.includes('proxy')) return '🌐'
  if (signal.includes('emulator') || signal.includes('rooted') || signal.includes('device')) return '📱'
  if (signal.includes('velocity') || signal.includes('burst') || signal.includes('Rapid')) return '⚡'
  if (signal.includes('amount') || signal.includes('Amount') || signal.includes('round')) return '💰'
  if (signal.includes('merchant') || signal.includes('Merchant') || signal.includes('gambling')) return '🏪'
  if (signal.includes('travel') || signal.includes('region') || signal.includes('geo')) return '🌍'
  return '⚠️'
}

export function AlertDetailPanel({ alert, onClose, onAction }: AlertDetailPanelProps) {
  const [actionTaken, setActionTaken] = useState<string | null>(null)
  const [localDecision, setLocalDecision] = useState<string>(alert.decision)

  function handleAction(action: string) {
    setActionTaken(action)
    setLocalDecision(action)
    onAction(alert.id, action)
  }
  const topModule = alert.sub_scores
    ? Object.entries(alert.sub_scores).sort(([, a], [, b]) => b - a)[0]
    : null

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-lg overflow-hidden sticky top-6">
      {/* Header */}
      <div className="bg-gray-900 text-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wider">Transaction Detail</p>
            <p className="font-mono text-sm mt-1">{alert.transaction_id}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl leading-none">&times;</button>
        </div>
      </div>

      <div className="p-6 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
        {/* Risk Score Hero */}
        <div className="text-center py-4">
          <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full border-4 ${
            alert.risk_score > 80 ? 'border-red-200 bg-red-50' :
            alert.risk_score > 60 ? 'border-orange-200 bg-orange-50' :
            alert.risk_score > 30 ? 'border-yellow-200 bg-yellow-50' :
            'border-green-200 bg-green-50'
          }`}>
            <span className={`text-3xl font-bold ${getScoreTextColor(alert.risk_score)}`}>
              {alert.risk_score.toFixed(1)}
            </span>
          </div>
          <p className="mt-2 text-sm text-gray-500">Risk Score / 100</p>
          {(() => {
            const badge = getRiskLevelBadge(alert.risk_score, localDecision, actionTaken || alert.analyst_action)
            return (
              <div className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-bold ${badge.style}`}>
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
              {alert.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase">User</p>
            <p className="font-mono font-semibold text-gray-900 mt-0.5">{alert.user_id}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase">Merchant</p>
            <p className="font-mono font-semibold text-gray-900 mt-0.5">{alert.merchant_id}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs uppercase">Time</p>
            <p className="font-semibold text-gray-900 mt-0.5">
              {new Date(alert.decided_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Module Scores Breakdown */}
        {alert.sub_scores && (
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Risk Score Breakdown</h3>
            <div className="space-y-3">
              {Object.entries(alert.sub_scores)
                .sort(([, a], [, b]) => b - a)
                .map(([module, score]) => {
                  const info = moduleLabels[module] || { name: module, description: '' }
                  const weight = { behavior_analyzer: 25, velocity_detector: 20, device_risk: 20, merchant_risk: 15, geolocation: 10, ip_intelligence: 10 }[module] || 0
                  const contribution = (score * weight / 100).toFixed(1)
                  return (
                    <div key={module} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <div>
                          <span className="text-sm font-medium text-gray-900">{info.name}</span>
                          <span className="text-xs text-gray-400 ml-2">({weight}% weight)</span>
                        </div>
                        <div className="text-right">
                          <span className={`text-sm font-bold ${getScoreTextColor(score)}`}>{score.toFixed(1)}/100</span>
                          <span className="text-xs text-gray-400 ml-1">+{contribution}</span>
                        </div>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getScoreColor(score)}`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{info.description}</p>
                    </div>
                  )
                })}
            </div>
            {topModule && (
              <p className="mt-3 text-xs text-gray-500">
                Primary risk driver: <strong>{moduleLabels[topModule[0]]?.name || topModule[0]}</strong> (score: {topModule[1].toFixed(0)})
              </p>
            )}
          </div>
        )}

        {/* Signals */}
        {alert.signals && alert.signals.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Fraud Signals ({alert.signals.length})
            </h3>
            <div className="space-y-2">
              {alert.signals.map((signal, i) => (
                <div key={i} className="flex items-start gap-2 text-sm bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                  <span className="flex-shrink-0">{getSignalIcon(signal)}</span>
                  <span className="text-gray-700">{signal}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Explanation */}
        {alert.explanation && (
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-2">AI Explanation</h3>
            <p className="text-sm text-gray-600 bg-blue-50 border border-blue-100 rounded-lg p-3">
              {alert.explanation}
            </p>
          </div>
        )}

        {/* Analyst Actions */}
        {(!actionTaken && !alert.analyst_action) && (
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Analyst Actions</h3>
            <div className="flex gap-2">
              <button
                onClick={() => handleAction('approve')}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
              >
                Approve
              </button>
              {alert.decision !== 'escalate' && (
                <button
                  onClick={() => handleAction('escalate')}
                  className="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors"
                >
                  Escalate
                </button>
              )}
              <button
                onClick={() => handleAction('block')}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
              >
                Block
              </button>
            </div>
          </div>
        )}

        {(actionTaken || (alert.analyst_action && alert.decision !== 'escalate')) && (
          <div className="border-t pt-4">
            {(() => {
              const action = actionTaken || alert.analyst_action
              const badge = getRiskLevelBadge(alert.risk_score, localDecision, action)
              return (
                <div className={`rounded-lg p-4 text-center ${
                  action === 'block' ? 'bg-red-50 border border-red-200' :
                  action === 'approve' ? 'bg-green-50 border border-green-200' :
                  'bg-orange-50 border border-orange-200'
                }`}>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${badge.style}`}>
                    {badge.label}
                  </span>
                  {alert.analyst_notes && (
                    <p className="text-sm text-gray-600 mt-2">{alert.analyst_notes}</p>
                  )}
                </div>
              )
            })()}
          </div>
        )}
      </div>
    </div>
  )
}
