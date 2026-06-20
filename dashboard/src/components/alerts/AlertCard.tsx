import { Alert } from '../../types'
import { AlertActions } from './AlertActions'

interface AlertCardProps {
  alert: Alert
  onAction: (alertId: string, action: string, notes?: string) => void
  onSelect?: (alert: Alert) => void
  isSelected?: boolean
}

function getRiskColor(score: number): string {
  if (score > 80) return 'text-red-600'
  if (score > 60) return 'text-orange-600'
  if (score > 30) return 'text-yellow-600'
  return 'text-green-600'
}

function getRiskLevelBadge(score: number, decision: string, analystAction?: string | null) {
  if (analystAction === 'block') return { style: 'bg-red-700 text-white ring-2 ring-red-300', label: 'BLOCKED BY ANALYST' }
  if (analystAction === 'approve') return { style: 'bg-green-200 text-green-800', label: 'APPROVED BY ANALYST' }
  if (analystAction === 'escalate') return { style: 'bg-orange-200 text-orange-800', label: 'ESCALATED BY ANALYST' }
  if (score > 80) return { style: 'bg-red-600 text-white animate-pulse', label: 'CRITICAL RISK' }
  if (decision === 'escalate') return { style: 'bg-orange-100 text-orange-700', label: 'ESCALATED' }
  if (decision === 'verify') return { style: 'bg-yellow-100 text-yellow-700', label: 'VERIFY' }
  return { style: 'bg-green-100 text-green-700', label: 'APPROVED' }
}

export function AlertCard({ alert, onAction, onSelect, isSelected }: AlertCardProps) {
  const badge = getRiskLevelBadge(alert.risk_score, alert.decision, alert.analyst_action)

  const borderStyle = alert.analyst_action === 'block'
    ? 'border-l-4 border-l-red-600'
    : alert.risk_score > 80
      ? 'border-l-4 border-l-red-500'
      : alert.risk_score > 60
        ? 'border-l-4 border-l-orange-400'
        : ''

  const bgStyle = isSelected
    ? 'bg-blue-50 border-blue-300 shadow-md'
    : alert.analyst_action === 'block'
      ? 'bg-red-100 border-2 border-red-400'
      : alert.analyst_action === 'approve'
        ? 'bg-green-50 border-green-200 shadow-sm'
        : alert.risk_score > 80
          ? 'bg-red-50/50 border-red-200 shadow-sm hover:border-red-300 hover:shadow'
          : 'bg-white border-gray-200 shadow-sm hover:border-blue-200 hover:shadow'

  return (
    <div
      data-testid="alert-card"
      onClick={() => onSelect?.(alert)}
      className={`p-4 rounded-lg border transition-all cursor-pointer ${borderStyle} ${bgStyle}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`px-2.5 py-1 rounded text-xs font-bold ${badge.style}`}>
            {badge.label}
          </span>
          <div>
            <p className="font-mono text-sm text-gray-900">{alert.transaction_id}</p>
            <p className="text-xs text-gray-500 mt-0.5">
              User: {alert.user_id} &middot; Merchant: {alert.merchant_id}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className={`text-lg font-bold ${getRiskColor(alert.risk_score)}`}>
              {alert.risk_score.toFixed(1)}
            </p>
            <p className="text-xs text-gray-400">risk score</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold text-gray-900">
              {alert.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
            </p>
          </div>
          {(!alert.analyst_action) && (
            <div onClick={(e) => e.stopPropagation()}>
              <AlertActions alertId={alert.id} decision={alert.decision} onAction={onAction} />
            </div>
          )}
        </div>
      </div>
      {/* Signal preview */}
      {alert.signals && alert.signals.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {alert.signals.slice(0, 3).map((signal, i) => (
            <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
              {signal}
            </span>
          ))}
          {alert.signals.length > 3 && (
            <span className="text-xs text-gray-400">+{alert.signals.length - 3} more</span>
          )}
        </div>
      )}
    </div>
  )
}
