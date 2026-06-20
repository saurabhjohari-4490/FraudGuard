"""Metrics schemas."""

from pydantic import BaseModel


class RecentTransaction(BaseModel):
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float
    risk_score: float
    decision: str
    signals: list[str]
    decided_at: str
    analyst_action: str | None = None


class TopRiskyUser(BaseModel):
    user_id: str
    transaction_count: int
    avg_risk_score: float
    total_amount: float
    last_decision: str


class MetricsResponse(BaseModel):
    total_transactions: int
    fraud_rate: float
    false_positive_rate: float
    avg_risk_score: float
    avg_latency_ms: float
    decisions: dict[str, int]
    score_distribution: list[dict[str, int | str]]
    throughput_tps: float
    critical_count: int  # score >= 80 (critical risk, needs immediate analyst action)
    blocked_count: int   # manually blocked by analyst
    review_count: int    # escalated (score 60-80)
    verify_count: int
    approved_count: int
    high_risk_count: int
    total_amount_at_risk: float
    reviewed_by_analyst: int
    pending_review: int
    recent_high_risk: list[RecentTransaction]
    top_risky_users: list[TopRiskyUser]
