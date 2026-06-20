import { Alert } from '../../types'
import { AlertCard } from './AlertCard'

interface AlertsQueueProps {
  alerts: Alert[]
  loading: boolean
  onAction: (alertId: string, action: string, notes?: string) => void
  onSelect?: (alert: Alert) => void
  selectedId?: string
}

export function AlertsQueue({ alerts, loading, onAction, onSelect, selectedId }: AlertsQueueProps) {
  if (loading) {
    return (
      <div className="space-y-3" data-testid="alerts-queue">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse h-20 bg-gray-200 rounded-lg" />
        ))}
      </div>
    )
  }

  if (alerts.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500" data-testid="alerts-queue">
        No alerts to display
      </div>
    )
  }

  return (
    <div className="space-y-3" data-testid="alerts-queue">
      {alerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onAction={onAction}
          onSelect={onSelect}
          isSelected={selectedId === alert.id}
        />
      ))}
    </div>
  )
}
