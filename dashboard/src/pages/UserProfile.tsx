import { useParams, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { UserRiskProfile } from '../types'
import { ArrowLeft, Shield, ShieldAlert, ShieldOff, AlertTriangle } from 'lucide-react'

export function UserProfile() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const [profile, setProfile] = useState<UserRiskProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!userId) return
    setLoading(true)
    api.get(`/api/v1/users/${userId}/risk-profile`)
      .then((res) => setProfile(res.data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false))
  }, [userId])

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse h-8 w-48 bg-gray-200 rounded" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse h-24 bg-gray-200 rounded-lg" />
          ))}
        </div>
        <div className="animate-pulse h-64 bg-gray-200 rounded-lg" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="space-y-4">
        <button onClick={() => navigate('/users')} className="flex items-center gap-1 text-blue-600 hover:text-blue-800">
          <ArrowLeft className="w-4 h-4" /> Back to Users
        </button>
        <div className="p-4 bg-yellow-50 text-yellow-700 rounded-lg">User not found</div>
      </div>
    )
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'critical':
        return (
          <div className="flex items-center gap-2">
            <ShieldOff className="w-5 h-5 text-red-500" />
            <span className="px-3 py-1 text-sm font-semibold rounded-full bg-red-100 text-red-700">Critical</span>
          </div>
        )
      case 'high':
        return (
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-orange-500" />
            <span className="px-3 py-1 text-sm font-semibold rounded-full bg-orange-100 text-orange-700">High</span>
          </div>
        )
      case 'medium':
        return (
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            <span className="px-3 py-1 text-sm font-semibold rounded-full bg-yellow-100 text-yellow-700">Medium</span>
          </div>
        )
      default:
        return (
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-green-500" />
            <span className="px-3 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-700">Low</span>
          </div>
        )
    }
  }

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'block':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-700">Block</span>
      case 'escalate':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-orange-100 text-orange-700">Escalate</span>
      case 'verify':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-yellow-100 text-yellow-700">Verify</span>
      case 'approve':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700">Approve</span>
      default:
        return <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-700">{decision}</span>
    }
  }

  const getRiskScoreColor = (score: number | null) => {
    if (!score) return 'text-gray-400'
    if (score >= 81) return 'text-red-600 font-semibold'
    if (score >= 61) return 'text-orange-600 font-semibold'
    if (score >= 31) return 'text-yellow-600'
    return 'text-green-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/users')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">User: <span className="font-mono">{userId}</span></h1>
        </div>
        {getRiskBadge(profile.risk_level)}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Total Transactions</p>
          <p className="text-2xl font-bold">{profile.transaction_count}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Avg Amount</p>
          <p className="text-2xl font-bold">
            {profile.avg_transaction_amount?.toLocaleString('en-IN', {
              style: 'currency',
              currency: 'INR',
              maximumFractionDigits: 0,
            }) ?? 'N/A'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Avg Risk Score</p>
          <p className={`text-2xl font-bold ${getRiskScoreColor(profile.avg_risk_score)}`}>
            {profile.avg_risk_score}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Max Risk Score</p>
          <p className={`text-2xl font-bold ${getRiskScoreColor(profile.max_risk_score)}`}>
            {profile.max_risk_score}
          </p>
        </div>
      </div>

      {/* Decision Distribution */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Decision Distribution</h3>
        <div className="flex gap-4 flex-wrap">
          {Object.entries(profile.decision_distribution).map(([decision, count]) => (
            <div key={decision} className="flex items-center gap-2">
              {getDecisionBadge(decision)}
              <span className="text-sm font-medium text-gray-700">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Typical Merchants */}
      {profile.typical_merchants.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-3">Typical Merchants</h3>
          <div className="flex gap-2 flex-wrap">
            {profile.typical_merchants.map((m) => (
              <span key={m} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-mono">
                {m}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recent Transactions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="font-semibold mb-4">Recent Transactions</h3>
        {profile.recent_transactions.length === 0 ? (
          <p className="text-gray-500">No transactions found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr>
                  <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">Transaction ID</th>
                  <th className="text-right px-3 py-2 text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="text-center px-3 py-2 text-xs font-medium text-gray-500 uppercase">Risk Score</th>
                  <th className="text-center px-3 py-2 text-xs font-medium text-gray-500 uppercase">Decision</th>
                  <th className="text-right px-3 py-2 text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {profile.recent_transactions.map((txn) => (
                  <tr key={txn.transaction_id} className="hover:bg-gray-50">
                    <td className="px-3 py-2 text-sm font-mono">{txn.transaction_id.slice(0, 16)}...</td>
                    <td className="px-3 py-2 text-sm text-right">
                      {txn.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}
                    </td>
                    <td className={`px-3 py-2 text-sm text-center ${getRiskScoreColor(txn.risk_score)}`}>
                      {txn.risk_score ?? '-'}
                    </td>
                    <td className="px-3 py-2 text-center">{getDecisionBadge(txn.decision)}</td>
                    <td className="px-3 py-2 text-xs text-right text-gray-400">
                      {new Date(txn.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
