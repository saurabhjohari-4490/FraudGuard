export interface Transaction {
  transaction_id: string
  user_id: string
  merchant_id: string
  amount: number
  currency: string
  device_fingerprint?: string
  ip_address?: string
  geo_lat?: number
  geo_lon?: number
  channel?: string
  created_at: string
  decision?: string
  risk_score?: number
}

export interface FraudDecision {
  transaction_id: string
  risk_score: number
  decision: 'approve' | 'verify' | 'escalate' | 'block'
  risk_level: 'critical' | 'high' | 'medium' | 'low'
  sub_scores: Record<string, number>
  signals: string[]
  explanation: string
  analyst_action?: string
  analyst_notes?: string
  decided_at: string
  reviewed_at?: string
}

export interface Alert extends FraudDecision {
  id: string
  amount: number
  user_id: string
  merchant_id: string
}

export interface RecentTransaction {
  transaction_id: string
  user_id: string
  merchant_id: string
  amount: number
  risk_score: number
  decision: string
  signals: string[]
  decided_at: string
  analyst_action?: string
}

export interface TopRiskyUser {
  user_id: string
  transaction_count: number
  avg_risk_score: number
  total_amount: number
  last_decision: string
}

export interface Metrics {
  total_transactions: number
  fraud_rate: number
  false_positive_rate: number
  avg_risk_score: number
  avg_latency_ms: number
  decisions: Record<string, number>
  score_distribution: { bucket: string; count: number }[]
  throughput_tps: number
  critical_count: number
  blocked_count: number
  review_count: number
  verify_count: number
  approved_count: number
  high_risk_count: number
  total_amount_at_risk: number
  reviewed_by_analyst: number
  pending_review: number
  recent_high_risk: RecentTransaction[]
  top_risky_users: TopRiskyUser[]
}

export interface MetricTransaction {
  id: string
  transaction_id: string
  user_id: string
  merchant_id: string
  amount: number
  risk_score: number
  decision: string
  signals: string[]
  sub_scores: Record<string, number>
  explanation: string
  analyst_action?: string
  decided_at: string
}

export interface UserRiskProfile {
  user_id: string
  risk_level: string
  transaction_count: number
  avg_transaction_amount: number | null
  avg_risk_score: number
  max_risk_score: number
  typical_merchants: string[]
  decision_distribution: Record<string, number>
  recent_transactions: {
    transaction_id: string
    amount: number
    decision: string
    risk_score: number | null
    created_at: string
  }[]
}
