import { Transaction } from '../../types'

interface TransactionListProps {
  transactions: Transaction[]
  loading: boolean
  onSelect: (txn: Transaction) => void
  selectedId?: string
}

export function TransactionList({ transactions, loading, onSelect, selectedId }: TransactionListProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(10)].map((_, i) => (
          <div key={i} className="animate-pulse h-12 bg-gray-200 rounded" />
        ))}
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 bg-white rounded-lg border">
        No transactions found. Try a different search.
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="text-left px-4 py-3 font-medium text-gray-600">Transaction ID</th>
            <th className="text-left px-4 py-3 font-medium text-gray-600">Amount</th>
            <th className="text-left px-4 py-3 font-medium text-gray-600">Score</th>
            <th className="text-left px-4 py-3 font-medium text-gray-600">Decision</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn) => (
            <tr
              key={txn.transaction_id}
              onClick={() => onSelect(txn)}
              className={`border-b cursor-pointer hover:bg-gray-50 ${
                selectedId === txn.transaction_id ? 'bg-blue-50' : ''
              }`}
            >
              <td className="px-4 py-3 font-mono text-xs">{txn.transaction_id.slice(0, 16)}...</td>
              <td className="px-4 py-3">{txn.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</td>
              <td className="px-4 py-3">{txn.risk_score?.toFixed(1) ?? '-'}</td>
              <td className="px-4 py-3">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  txn.decision === 'approve' ? 'bg-green-100 text-green-700' :
                  txn.decision === 'escalate' && txn.risk_score && txn.risk_score > 80 ? 'bg-red-100 text-red-700' :
                  txn.decision === 'escalate' ? 'bg-orange-100 text-orange-700' :
                  txn.decision === 'verify' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {txn.decision === 'escalate' && txn.risk_score && txn.risk_score > 80 ? 'critical' :
                   txn.decision || 'pending'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
