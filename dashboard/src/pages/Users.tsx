import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { Search, Shield, ShieldAlert, ShieldOff, ChevronRight } from 'lucide-react'

interface UserSummary {
  user_id: string
  transaction_count: number
  total_amount: number
  avg_amount: number
  avg_risk_score: number
  max_risk_score: number
  risk_level: string
  decision_counts: Record<string, number>
  last_active: string
}

export function Users() {
  const [users, setUsers] = useState<UserSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string> = { limit: '100' }
    if (search) params.search = search
    api.get<{ users: UserSummary[]; total: number }>('/api/v1/users', { params })
      .then((res) => setUsers(res.data.users))
      .catch(() => setUsers([]))
      .finally(() => setLoading(false))
  }, [search])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'critical':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 text-red-700">Critical</span>
      case 'high':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-orange-100 text-orange-700">High</span>
      case 'medium':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700">Medium</span>
      default:
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-700">Low</span>
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return <ShieldOff className="w-5 h-5 text-red-500" />
      case 'high':
        return <ShieldAlert className="w-5 h-5 text-orange-500" />
      default:
        return <Shield className="w-5 h-5 text-green-500" />
    }
  }

  const getRiskBarColor = (score: number) => {
    if (score >= 81) return 'bg-red-500'
    if (score >= 61) return 'bg-orange-500'
    if (score >= 31) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">User Profiles</h1>
        <span className="text-sm text-gray-500">{users.length} users</span>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by user ID..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
        {search && (
          <button
            type="button"
            onClick={() => { setSearch(''); setSearchInput('') }}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Clear
          </button>
        )}
      </form>

      {/* User List */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="animate-pulse h-16 bg-gray-200 rounded-lg" />
          ))}
        </div>
      ) : users.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {search ? `No users found matching "${search}"` : 'No users found'}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Avg Risk Score</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 uppercase">Transactions</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 uppercase">Avg Amount</th>
                <th className="text-center px-4 py-3 text-xs font-medium text-gray-500 uppercase">Decisions</th>
                <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 uppercase">Last Active</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((user) => (
                <tr
                  key={user.user_id}
                  onClick={() => navigate(`/users/${user.user_id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {getRiskIcon(user.risk_level)}
                      <span className="font-mono text-sm">{user.user_id}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">{getRiskBadge(user.risk_level)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${getRiskBarColor(user.avg_risk_score)}`}
                          style={{ width: `${Math.min(user.avg_risk_score, 100)}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{user.avg_risk_score}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right text-sm">{user.transaction_count}</td>
                  <td className="px-4 py-3 text-right text-sm">
                    {user.avg_amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-center gap-1">
                      {(user.decision_counts.block || 0) > 0 && (
                        <span className="px-1.5 py-0.5 text-xs bg-red-100 text-red-700 rounded">
                          {user.decision_counts.block} B
                        </span>
                      )}
                      {(user.decision_counts.escalate || 0) > 0 && (
                        <span className="px-1.5 py-0.5 text-xs bg-orange-100 text-orange-700 rounded">
                          {user.decision_counts.escalate} E
                        </span>
                      )}
                      {(user.decision_counts.verify || 0) > 0 && (
                        <span className="px-1.5 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded">
                          {user.decision_counts.verify} V
                        </span>
                      )}
                      {(user.decision_counts.approve || 0) > 0 && (
                        <span className="px-1.5 py-0.5 text-xs bg-green-100 text-green-700 rounded">
                          {user.decision_counts.approve} A
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right text-xs text-gray-400">
                    {user.last_active ? new Date(user.last_active).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-4 py-3">
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
