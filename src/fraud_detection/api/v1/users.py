"""Users API endpoint - risk profile."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from fraud_detection.db.session import get_db
from fraud_detection.models.fraud_decision import FraudDecision
from fraud_detection.models.transaction import Transaction

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _compute_risk_level(avg_risk_score: float) -> str:
    """Determine user risk level from avg risk score.

    Aligned with system-wide boundaries:
        > 80 = critical
        > 60 = high
        > 30 = medium
        else = low
    """
    if avg_risk_score > 80:
        return "critical"
    elif avg_risk_score > 60:
        return "high"
    elif avg_risk_score > 30:
        return "medium"
    return "low"


@router.get("")
async def list_users(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(None, description="Search by user ID prefix"),
) -> dict:
    """List all users with their risk summary (single optimized query)."""
    # Single query: join transactions + decisions, aggregate per user
    query = (
        select(
            Transaction.user_id,
            func.count(Transaction.transaction_id).label("txn_count"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.amount).label("avg_amount"),
            func.max(Transaction.created_at).label("last_active"),
            # Risk scores (only non-approved)
            func.avg(
                case(
                    (FraudDecision.decision != "approve", FraudDecision.risk_score),
                    else_=None,
                )
            ).label("avg_risk"),
            func.max(
                case(
                    (FraudDecision.decision != "approve", FraudDecision.risk_score),
                    else_=None,
                )
            ).label("max_risk"),
            # Decision counts
            func.count(
                case((FraudDecision.decision == "escalate", 1), else_=None)
            ).label("escalate_count"),
            func.count(
                case((FraudDecision.decision == "verify", 1), else_=None)
            ).label("verify_count"),
            func.count(
                case((FraudDecision.decision == "approve", 1), else_=None)
            ).label("approve_count"),
        )
        .outerjoin(FraudDecision, FraudDecision.transaction_id == Transaction.transaction_id)
        .group_by(Transaction.user_id)
    )

    if search:
        query = query.where(Transaction.user_id.ilike(f"%{search}%"))

    query = query.order_by(desc("last_active")).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    users = []
    for row in rows:
        decision_counts = {}
        if row.escalate_count:
            decision_counts["escalate"] = row.escalate_count
        if row.verify_count:
            decision_counts["verify"] = row.verify_count
        if row.approve_count:
            decision_counts["approve"] = row.approve_count

        avg_risk = round(float(row.avg_risk or 0), 1)
        users.append({
            "user_id": row.user_id,
            "transaction_count": row.txn_count,
            "total_amount": float(row.total_amount or 0),
            "avg_amount": round(float(row.avg_amount or 0), 2),
            "avg_risk_score": avg_risk,
            "max_risk_score": round(float(row.max_risk or 0), 1),
            "risk_level": _compute_risk_level(avg_risk),
            "decision_counts": decision_counts,
            "last_active": row.last_active.isoformat() if row.last_active else "",
        })

    return {"users": users, "total": len(users)}


@router.get("/{user_id}/risk-profile")
async def get_user_risk_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a user's risk profile including recent transactions and decisions.

    Optimized: 2 queries instead of 5 (single stats+risk query + recent txns with join).
    """
    # Query 1: All stats in one shot (count, avg amount, risk scores, decision counts)
    stats_result = await db.execute(
        select(
            func.count(Transaction.transaction_id).label("txn_count"),
            func.avg(Transaction.amount).label("avg_amount"),
            func.avg(
                case(
                    (FraudDecision.decision != "approve", FraudDecision.risk_score),
                    else_=None,
                )
            ).label("avg_risk"),
            func.max(
                case(
                    (FraudDecision.decision != "approve", FraudDecision.risk_score),
                    else_=None,
                )
            ).label("max_risk"),
            func.count(
                case((FraudDecision.decision == "escalate", 1), else_=None)
            ).label("escalate_count"),
            func.count(
                case((FraudDecision.decision == "verify", 1), else_=None)
            ).label("verify_count"),
            func.count(
                case((FraudDecision.decision == "approve", 1), else_=None)
            ).label("approve_count"),
        )
        .select_from(Transaction)
        .outerjoin(FraudDecision, FraudDecision.transaction_id == Transaction.transaction_id)
        .where(Transaction.user_id == user_id)
    )
    row = stats_result.one()

    if not row.txn_count:
        raise HTTPException(status_code=404, detail="User not found")

    decision_counts = {}
    if row.escalate_count:
        decision_counts["escalate"] = row.escalate_count
    if row.verify_count:
        decision_counts["verify"] = row.verify_count
    if row.approve_count:
        decision_counts["approve"] = row.approve_count

    # Query 2: Recent transactions with decisions (single join query)
    recent_result = await db.execute(
        select(Transaction, FraudDecision)
        .outerjoin(FraudDecision, FraudDecision.transaction_id == Transaction.transaction_id)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(20)
    )

    recent = []
    merchants_set = set()
    for txn, decision in recent_result.all():
        merchants_set.add(txn.merchant_id)
        recent.append({
            "transaction_id": txn.transaction_id,
            "amount": float(txn.amount),
            "decision": decision.decision if decision else "pending",
            "risk_score": float(decision.risk_score) if decision else None,
            "created_at": txn.created_at.isoformat(),
        })

    avg_risk = round(float(row.avg_risk or 0), 1)
    return {
        "user_id": user_id,
        "risk_level": _compute_risk_level(avg_risk),
        "transaction_count": row.txn_count,
        "avg_transaction_amount": round(float(row.avg_amount or 0), 2),
        "avg_risk_score": avg_risk,
        "max_risk_score": round(float(row.max_risk or 0), 1),
        "typical_merchants": list(merchants_set)[:10],
        "decision_distribution": decision_counts,
        "recent_transactions": recent,
    }
