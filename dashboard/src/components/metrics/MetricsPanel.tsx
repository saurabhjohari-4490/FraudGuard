import { Metrics } from '../../types'
import { Activity, AlertTriangle, CheckCircle, ShieldOff, ShieldAlert, Eye, Clock, Ban } from 'lucide-react'

interface MetricsPanelProps {
  metrics: Metrics | null
  loading: boolean
  onCardClick?: (drillDown: { category: string; title: string }) => void
}

interface MetricCardConfig {
  title: string
  value: string
  icon: React.ReactNode
  category: string
  variant?: 'default' | 'warning' | 'danger' | 'success'
  subtitle?: string
}

export function MetricsPanel({ metrics, loading, onCardClick }: MetricsPanelProps) {
  if (loading || !metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="animate-pulse h-28 bg-gray-200 rounded-lg" />
        ))}
      </div>
    )
  }

  const cards: MetricCardConfig[] = [
    {
      title: 'Total Transactions',
      value: metrics.total_transactions.toLocaleString(),
      icon: <Activity className="w-5 h-5 text-blue-500" />,
      category: 'all',
      subtitle: `${metrics.throughput_tps} TPS`,
    },
    {
      title: 'Critical Risk',
      value: metrics.critical_count.toLocaleString(),
      icon: <ShieldOff className="w-5 h-5 text-red-500" />,
      category: 'critical',
      variant: metrics.critical_count > 0 ? 'danger' : 'default',
      subtitle: `${(() => { const pct = (metrics.critical_count / Math.max(metrics.total_transactions, 1)) * 100; return pct >= 1 ? pct.toFixed(1) : pct > 0 ? pct.toFixed(2) : '0'; })()}% of total`,
    },
    {
      title: 'Escalated',
      value: metrics.review_count.toLocaleString(),
      icon: <Eye className="w-5 h-5 text-orange-500" />,
      category: 'escalate',
      variant: metrics.review_count > 10 ? 'warning' : 'default',
      subtitle: `${metrics.pending_review} pending analyst action`,
    },
    {
      title: 'Needs Verification',
      value: metrics.verify_count.toLocaleString(),
      icon: <ShieldAlert className="w-5 h-5 text-yellow-500" />,
      category: 'verify',
      subtitle: 'Step-up auth required',
    },
    {
      title: 'Approved',
      value: metrics.approved_count.toLocaleString(),
      icon: <CheckCircle className="w-5 h-5 text-green-500" />,
      category: 'approved',
      variant: 'success',
      subtitle: `${((metrics.approved_count / Math.max(metrics.total_transactions, 1)) * 100).toFixed(1)}% approval rate`,
    },
    {
      title: 'Fraud Rate / Amount at Risk',
      value: `${(metrics.fraud_rate * 100).toFixed(2)}%`,
      icon: <AlertTriangle className="w-5 h-5 text-red-500" />,
      category: 'fraud_rate',
      variant: metrics.fraud_rate > 0.05 ? 'danger' : 'default',
      subtitle: `${metrics.total_amount_at_risk.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })} at risk`,
    },
    {
      title: 'Blocked by Analyst',
      value: metrics.blocked_count.toLocaleString(),
      icon: <Ban className="w-5 h-5 text-red-700" />,
      category: 'blocked',
      variant: metrics.blocked_count > 0 ? 'danger' : 'default',
      subtitle: 'Manually blocked transactions',
    },
    {
      title: 'Analyst Reviewed',
      value: `${metrics.reviewed_by_analyst}`,
      icon: <Clock className="w-5 h-5 text-indigo-500" />,
      category: 'reviewed',
      subtitle: `${metrics.pending_review} still pending`,
    },
  ]

  const borderColors = {
    default: 'border-gray-200 hover:border-blue-300',
    warning: 'border-yellow-300 hover:border-yellow-400',
    danger: 'border-red-300 hover:border-red-400',
    success: 'border-green-200 hover:border-green-300',
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.category}
          onClick={() => onCardClick?.({ category: card.category, title: card.title })}
          className={`bg-white p-4 rounded-lg shadow-sm border cursor-pointer transition-all hover:shadow-md ${
            borderColors[card.variant || 'default']
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">{card.title}</span>
            {card.icon}
          </div>
          <p className="text-2xl font-bold text-gray-900">{card.value}</p>
          {card.subtitle && (
            <p className="text-xs text-gray-400 mt-1">{card.subtitle}</p>
          )}
        </div>
      ))}
    </div>
  )
}
