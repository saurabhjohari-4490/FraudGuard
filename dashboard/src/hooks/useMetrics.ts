import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import { Metrics } from '../types'

export function useMetrics(refreshInterval = 5000) {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await api.get<Metrics>('/api/v1/metrics')
      setMetrics(res.data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, refreshInterval)
    return () => clearInterval(interval)
  }, [fetchMetrics, refreshInterval])

  return { metrics, isLoading, error, refresh: fetchMetrics }
}
