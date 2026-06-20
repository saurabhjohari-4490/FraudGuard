import { useState, useRef, useEffect } from 'react'
import { AlertsQueue } from '../components/alerts/AlertsQueue'
import { AlertDetailPanel } from '../components/alerts/AlertDetailPanel'
import { useAlerts } from '../hooks/useAlerts'
import { Alert } from '../types'

export function Alerts() {
  const [filter, setFilter] = useState<string>('all')
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)
  const { alerts, isLoading, updateAlert, counts } = useAlerts(filter)
  const detailPanelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (selectedAlert && detailPanelRef.current && !detailPanelRef.current.contains(event.target as Node)) {
        setSelectedAlert(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [selectedAlert])

  const filters = [
    { key: 'all', label: 'All', count: counts.all },
    { key: 'critical', label: 'Critical Risk', count: counts.critical },
    { key: 'escalate', label: 'Escalate', count: counts.escalate },
    { key: 'verify', label: 'Verification Pending', count: counts.verify },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Fraud Alerts</h1>
        <div className="flex gap-2" data-testid="alert-status-filter">
          {filters.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                filter === f.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {f.label}
              <span className={`px-1.5 py-0.5 rounded-full text-xs font-semibold ${
                filter === f.key
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}>
                {f.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={selectedAlert ? 'lg:col-span-1' : 'lg:col-span-3'}>
          <AlertsQueue
            alerts={alerts}
            loading={isLoading}
            onAction={updateAlert}
            onSelect={setSelectedAlert}
            selectedId={selectedAlert?.id}
          />
        </div>
        {selectedAlert && (
          <div className="lg:col-span-2" ref={detailPanelRef}>
            <AlertDetailPanel
              alert={selectedAlert}
              onClose={() => setSelectedAlert(null)}
              onAction={updateAlert}
            />
          </div>
        )}
      </div>
    </div>
  )
}
