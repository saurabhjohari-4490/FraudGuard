import { useState } from 'react'
import { TransactionSearch } from '../components/transactions/TransactionSearch'
import { TransactionList } from '../components/transactions/TransactionList'
import { TransactionDetail } from '../components/transactions/TransactionDetail'
import { useTransactions } from '../hooks/useTransactions'
import { Transaction } from '../types'

export function Transactions() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selected, setSelected] = useState<Transaction | null>(null)
  const { transactions, isLoading, search } = useTransactions()

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    search(query)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
      <TransactionSearch value={searchQuery} onSearch={handleSearch} />
      {!searchQuery && !isLoading && transactions.length > 0 && (
        <p className="text-sm text-gray-500">Showing 10 most recent transactions</p>
      )}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={selected ? 'lg:col-span-2' : 'lg:col-span-3'}>
          <TransactionList
            transactions={transactions}
            loading={isLoading}
            onSelect={setSelected}
            selectedId={selected?.transaction_id}
          />
        </div>
        {selected && (
          <div>
            <TransactionDetail transaction={selected} />
          </div>
        )}
      </div>
    </div>
  )
}
