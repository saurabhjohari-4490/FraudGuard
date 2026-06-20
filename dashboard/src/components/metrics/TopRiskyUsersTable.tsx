import { TopRiskyUser } from '../../types'
import { useNavigate } from 'react-router-dom'

interface TopRiskyUsersTableProps {
  users: TopRiskyUser[]
  loading: boolean
}

function getRiskBadge(score: number) {
  if (score >= 70) return 'bg-red-100 text-red-700'
  if (score >= 40) return 'bg-orange-100 text-orange-700'
  if (score >= 20) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

function getDecisionBadge(decision: string) {
  const styles: Record<string, string> = {
    block: 'bg-red-200 text-red-800',
    escalate: 'bg-orange-100 text-orange-700',
    verify: 'bg-yellow-100 text-yellow-700',
    approve: 'bg-green-100 text-green-700',
  }
  return styles[decision] || 'bg-gray-100 text-gray-700'
}

function getDecisionLabel(decision: string, score: number) {
  if (decision === 'escalate' && score > 80) return 'CRITICAL'
  if (decision === 'block') return 'BLOCKED'
  return decision.toUpperCase()
}

export function TopRiskyUsersTable({ users, loading }: TopRiskyUsersTableProps) {
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Top Risky Users</h3>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse h-10 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (users.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Top Risky Users</h3>
        <p className="text-gray-400 text-sm text-center py-8">No data yet</p>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="font-semibold mb-4">Top Risky Users</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="pb-2 font-medium">User</th>
              <th className="pb-2 font-medium">Txns</th>
              <th className="pb-2 font-medium">Avg Score</th>
              <th className="pb-2 font-medium">Amount</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr
                key={user.user_id}
                onClick={() => navigate(`/users/${user.user_id}`)}
                className="border-b last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="py-2.5 font-mono text-xs">{user.user_id}</td>
                <td className="py-2.5">{user.transaction_count}</td>
                <td className="py-2.5">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getRiskBadge(user.avg_risk_score)}`}>
                    {user.avg_risk_score.toFixed(1)}
                  </span>
                </td>
                <td className="py-2.5 font-medium">
                  {user.total_amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })}
                </td>
                <td className="py-2.5">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getDecisionBadge(user.last_decision)}`}>
                    {getDecisionLabel(user.last_decision, user.avg_risk_score)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
