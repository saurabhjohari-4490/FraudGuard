import { useState, useEffect, useCallback, useMemo } from 'react'
import { api } from '../api/client'
import { Alert } from '../types'

interface AlertCounts {
  all: number
  critical: number
  escalate: number
  verify: number
}

export function useAlerts(filter = 'all') {
  const [allAlerts, setAllAlerts] = useState<Alert[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [counts, setCounts] = useState<AlertCounts>({ all: 0, critical: 0, escalate: 0, verify: 0 })
  const [isLoading, setIsLoading] = useState(true)

  const fetchAlerts = useCallback(async () => {
    try {
      const params: Record<string, string | number> = { limit: 500 }
      if (filter && filter !== 'all') {
        params.decision = filter
      }
      const res = await api.get<{ alerts: Alert[]; total: number; counts: AlertCounts }>('/api/v1/alerts', {
        params,
      })
      setAllAlerts(res.data.alerts)
      setTotalCount(res.data.total)
      setCounts(res.data.counts)
    } catch {
      setAllAlerts([])
      setTotalCount(0)
      setCounts({ all: 0, critical: 0, escalate: 0, verify: 0 })
    } finally {
      setIsLoading(false)
    }
  }, [filter])

  useEffect(() => {
    fetchAlerts()
    const interval = setInterval(fetchAlerts, 10000)
    return () => clearInterval(interval)
  }, [fetchAlerts])

  const alerts = useMemo(() => {
    if (filter === 'all') {
      // Sort: critical first, then by risk score desc
      return [...allAlerts].sort((a, b) => {
        const aIsCritical = a.risk_level === 'critical' ? 0 : 1
        const bIsCritical = b.risk_level === 'critical' ? 0 : 1
        if (aIsCritical !== bIsCritical) return aIsCritical - bIsCritical
        return b.risk_score - a.risk_score
      })
    }
    return allAlerts
  }, [allAlerts, filter])

  const updateAlert = async (alertId: string, action: string, notes?: string) => {
    // Immediately update the local state for instant UI feedback
    setAllAlerts((prev) =>
      prev.map((a) => {
        if (a.id !== alertId) return a
        return { ...a, analyst_action: action }
      })
    )

    // Persist to backend, then refresh after delay to avoid race condition
    await api.patch(`/api/v1/alerts/${alertId}`, { analyst_action: action, analyst_notes: notes })
    setTimeout(fetchAlerts, 1500)
  }

  return { alerts, isLoading, updateAlert, refresh: fetchAlerts, counts, totalCount }
}
