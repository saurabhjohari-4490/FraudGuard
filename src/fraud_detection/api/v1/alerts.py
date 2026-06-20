"""Alerts API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from fraud_detection.db.session import get_db
from fraud_detection.models.fraud_decision import FraudDecision
from fraud_detection.models.transaction import Transaction
from fraud_detection.schemas.alert import AlertCountsResponse, AlertListResponse, AlertResponse, AlertUpdateRequest
from fraud_detection.services.decision_engine import DecisionEngine

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


def _compute_risk_level(score: float) -> str:
    """Compute risk level from score."""
    return DecisionEngine.compute_risk_level(score)


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    decision: str | None = None,
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> AlertListResponse:
    """List fraud alerts (decisions that need review).

    Filters:
        - all: all actionable alerts (escalate + verify)
        - critical: risk_score >= 80 (highest priority)
        - escalate: risk_score 60-80
        - verify: risk_score 30-60
        - block: manually blocked by analyst
    """
    query = (
        select(FraudDecision, Transaction)
        .join(Transaction, FraudDecision.transaction_id == Transaction.transaction_id)
    )

    if decision == "critical":
        # Critical = escalated with score > 80
        query = query.where(
            and_(
                FraudDecision.decision == "escalate",
                FraudDecision.risk_score > 80,
            )
        )
        query = query.order_by(FraudDecision.risk_score.desc())
    elif decision == "escalate":
        # Regular escalate = score 61-80
        query = query.where(
            and_(
                FraudDecision.decision == "escalate",
                FraudDecision.risk_score <= 80,
            )
        )
        query = query.order_by(FraudDecision.risk_score.desc())
    elif decision == "verify":
        query = query.where(FraudDecision.decision == "verify")
        query = query.order_by(FraudDecision.risk_score.desc())
    elif decision == "block":
        # Block = manually blocked by analyst
        query = query.where(FraudDecision.decision == "block")
        query = query.order_by(FraudDecision.risk_score.desc())
    else:
        # All actionable alerts (escalate + verify), sorted by risk
        query = query.where(FraudDecision.decision.in_(["escalate", "verify"]))
        query = query.order_by(FraudDecision.risk_score.desc())

    result = await db.execute(query.limit(limit))
    rows = result.all()

    alerts = []
    for fraud_decision, transaction in rows:
        alerts.append(AlertResponse(
            id=str(fraud_decision.id),
            transaction_id=fraud_decision.transaction_id,
            user_id=transaction.user_id,
            merchant_id=transaction.merchant_id,
            amount=float(transaction.amount),
            risk_score=float(fraud_decision.risk_score),
            decision=fraud_decision.decision,
            risk_level=_compute_risk_level(float(fraud_decision.risk_score)),
            sub_scores=fraud_decision.sub_scores,
            signals=fraud_decision.signals,
            explanation=fraud_decision.explanation or "",
            analyst_action=fraud_decision.analyst_action,
            analyst_notes=fraud_decision.analyst_notes,
            decided_at=fraud_decision.decided_at,
        ))

    # Per-category counts
    # Critical: escalate with score > 80
    critical_count_result = await db.execute(
        select(func.count())
        .where(FraudDecision.decision == "escalate")
        .where(FraudDecision.risk_score > 80)
    )
    critical_count = critical_count_result.scalar() or 0

    # Escalate: escalate with score <= 80
    escalate_count_result = await db.execute(
        select(func.count())
        .where(FraudDecision.decision == "escalate")
        .where(FraudDecision.risk_score <= 80)
    )
    escalate_count = escalate_count_result.scalar() or 0

    # Verify
    verify_count_result = await db.execute(
        select(func.count())
        .where(FraudDecision.decision == "verify")
    )
    verify_count = verify_count_result.scalar() or 0

    total = critical_count + escalate_count + verify_count

    counts = AlertCountsResponse(
        all=total,
        critical=critical_count,
        escalate=escalate_count,
        verify=verify_count,
    )

    return AlertListResponse(alerts=alerts, total=total, counts=counts)


@router.patch("/{alert_id}")
async def update_alert(
    alert_id: str,
    payload: AlertUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update an alert with analyst action.

    Block is a manual-only action - only analysts can block transactions.
    """
    valid_actions = ("approve", "escalate", "block")

    result = await db.execute(
        select(FraudDecision).where(FraudDecision.id == alert_id)
    )
    fraud_decision = result.scalar_one_or_none()
    if not fraud_decision:
        raise HTTPException(status_code=404, detail="Alert not found")

    if payload.analyst_action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}",
        )

    fraud_decision.analyst_action = payload.analyst_action
    fraud_decision.analyst_notes = payload.analyst_notes
    fraud_decision.reviewed_at = datetime.utcnow()

    # Update the decision based on analyst action
    if payload.analyst_action == "block":
        fraud_decision.decision = "block"
    elif payload.analyst_action == "approve":
        fraud_decision.decision = "approve"
    elif payload.analyst_action == "escalate":
        fraud_decision.decision = "escalate"

    return {
        "status": "updated",
        "alert_id": alert_id,
        "action": payload.analyst_action,
        "decision": fraud_decision.decision,
    }
