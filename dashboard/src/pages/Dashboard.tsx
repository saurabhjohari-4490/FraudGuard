import { useState } from 'react'
import { MetricsPanel } from '../components/metrics/MetricsPanel'
import { RiskDistribution } from '../components/metrics/RiskDistribution'
import { DecisionPieChart } from '../components/metrics/DecisionPieChart'
import { TopRiskyUsersTable } from '../components/metrics/TopRiskyUsersTable'
import { RecentHighRiskList } from '../components/metrics/RecentHighRiskList'
import { TransactionDrillDown } from '../components/metrics/TransactionDrillDown'
import { useMetrics } from '../hooks/useMetrics'

export function Dashboard() {
  const { metrics, isLoading, error } = useMetrics()
  const [drillDown, setDrillDown] = useState<{ category: string; title: string } | null>(null)

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-lg">
        Failed to load metrics: {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        {drillDown && (
          <button
            onClick={() => setDrillDown(null)}
            className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            &larr; Back to Overview
          </button>
        )}
      </div>

      {drillDown ? (
        <TransactionDrillDown category={drillDown.category} title={drillDown.title} />
      ) : (
        <>
          <MetricsPanel metrics={metrics} loading={isLoading} onCardClick={setDrillDown} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskDistribution data={metrics?.score_distribution} />
            <DecisionPieChart decisions={metrics?.decisions} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RecentHighRiskList
              transactions={metrics?.recent_high_risk || []}
              loading={isLoading}
            />
            <TopRiskyUsersTable
              users={metrics?.top_risky_users || []}
              loading={isLoading}
            />
          </div>
        </>
      )}
    </div>
  )
}
