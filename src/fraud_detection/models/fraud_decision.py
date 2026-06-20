"""Fraud decision model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from fraud_detection.models.base import Base, UUIDMixin


class FraudDecision(UUIDMixin, Base):
    __tablename__ = "fraud_decisions"

    transaction_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("transactions.transaction_id"), nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    sub_scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    signals: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    explanation: Mapped[str | None] = mapped_column(Text)
    analyst_action: Mapped[str | None] = mapped_column(String(16))
    analyst_notes: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_fraud_decisions_decision", "decision"),
        Index("idx_fraud_decisions_risk_score", "risk_score"),
    )
