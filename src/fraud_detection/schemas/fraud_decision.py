"""Fraud decision schemas."""

from datetime import datetime

from pydantic import BaseModel


class FraudDecisionResponse(BaseModel):
    """Response schema for fraud decision lookup."""

    transaction_id: str
    risk_score: float
    decision: str
    sub_scores: dict[str, float]
    signals: list[str]
    explanation: str
    analyst_action: str | None = None
    analyst_notes: str | None = None
    decided_at: datetime
    reviewed_at: datetime | None = None

    model_config = {"from_attributes": True}
