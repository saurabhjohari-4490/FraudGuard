"""Fraud decision lookup endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fraud_detection.db.session import get_db
from fraud_detection.models.fraud_decision import FraudDecision
from fraud_detection.schemas.fraud_decision import FraudDecisionResponse

router = APIRouter(prefix="/api/v1/fraud", tags=["fraud"])


@router.get("/{transaction_id}", response_model=FraudDecisionResponse)
async def get_fraud_decision(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> FraudDecisionResponse:
    """Get the fraud decision for a specific transaction."""
    result = await db.execute(
        select(FraudDecision).where(FraudDecision.transaction_id == transaction_id)
    )
    decision = result.scalar_one_or_none()
    if not decision:
        raise HTTPException(status_code=404, detail="Fraud decision not found")

    return FraudDecisionResponse(
        transaction_id=decision.transaction_id,
        risk_score=float(decision.risk_score),
        decision=decision.decision,
        sub_scores=decision.sub_scores,
        signals=decision.signals,
        explanation=decision.explanation or "",
        analyst_action=decision.analyst_action,
        analyst_notes=decision.analyst_notes,
        decided_at=decision.decided_at,
        reviewed_at=decision.reviewed_at,
    )
