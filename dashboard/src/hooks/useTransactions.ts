import { useState, useCallback, useEffect } from 'react'
import { api } from '../api/client'
import { Transaction } from '../types'

export function useTransactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Load recent 10 transactions on mount
  useEffect(() => {
    async function fetchRecent() {
      try {
        const res = await api.get<{ transactions: Transaction[] }>('/api/v1/transactions', {
          params: { limit: 10 },
        })
        setTransactions(res.data.transactions)
      } catch {
        setTransactions([])
      } finally {
        setIsLoading(false)
      }
    }
    fetchRecent()
  }, [])

  const search = useCallback(async (query: string) => {
    setIsLoading(true)
    try {
      const res = await api.get<{ transactions: Transaction[] }>('/api/v1/transactions', {
        params: { q: query || undefined, limit: query ? 200 : 10 },
      })
      setTransactions(res.data.transactions)
    } catch {
      setTransactions([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { transactions, isLoading, search }
}
