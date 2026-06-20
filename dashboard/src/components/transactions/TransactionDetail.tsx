import { useEffect, useState } from 'react'
import { api } from '../../api/client'
import { Transaction, FraudDecision } from '../../types'
import { RiskBreakdown } from './RiskBreakdown'

interface TransactionDetailProps {
  transaction: Transaction
}

export function TransactionDetail({ transaction }: TransactionDetailProps) {
  const [decision, setDecision] = useState<FraudDecision | null>(null)

  useEffect(() => {
    api.get<FraudDecision>(`/api/v1/fraud/${transaction.transaction_id}`)
      .then((res) => setDecision(res.data))
      .catch(() => setDecision(null))
  }, [transaction.transaction_id])

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border space-y-4">
      <h3 className="font-semibold text-lg">Transaction Detail</h3>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">ID</span>
          <span className="font-mono text-xs">{transaction.transaction_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">User</span>
          <span>{transaction.user_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Merchant</span>
          <span>{transaction.merchant_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Amount</span>
          <span className="font-semibold">
            {transaction.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">IP Address</span>
          <span>{transaction.ip_address || 'N/A'}</span>
        </div>
      </div>

      {decision && (
        <>
          <hr />
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-500 text-sm">Risk Score</span>
              <span className="text-2xl font-bold">{decision.risk_score.toFixed(1)}</span>
            </div>
            <RiskBreakdown subScores={decision.sub_scores} />
          </div>

          {decision.signals.length > 0 && (
            <>
              <hr />
              <div>
                <p className="text-sm font-medium mb-2">Signals</p>
                <ul className="space-y-1">
                  {decision.signals.map((signal, i) => (
                    <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                      <span className="text-red-400 mt-0.5">!</span>
                      {signal}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}

          {decision.explanation && (
            <>
              <hr />
              <p className="text-sm text-gray-600 italic">{decision.explanation}</p>
            </>
          )}
        </>
      )}
    </div>
  )
}
