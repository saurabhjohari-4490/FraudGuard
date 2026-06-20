"""Alert schemas."""

from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float
    risk_score: float
    decision: str
    risk_level: str  # critical, high, medium, low
    sub_scores: dict[str, float]
    signals: list[str]
    explanation: str
    analyst_action: str | None = None
    analyst_notes: str | None = None
    decided_at: datetime


class AlertCountsResponse(BaseModel):
    all: int = 0
    critical: int = 0  # score >= 80 (requires immediate action)
    escalate: int = 0  # score 60-80
    verify: int = 0    # score 30-60


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    counts: AlertCountsResponse = AlertCountsResponse()


class AlertUpdateRequest(BaseModel):
    analyst_action: str  # approve, escalate, dismiss
    analyst_notes: str | None = None
