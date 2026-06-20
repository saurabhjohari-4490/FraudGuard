"""Metrics API endpoint."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, case, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from fraud_detection.db.session import get_db
from fraud_detection.models.fraud_decision import FraudDecision
from fraud_detection.models.transaction import Transaction
from fraud_detection.schemas.metrics import MetricsResponse, RecentTransaction, TopRiskyUser

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)) -> MetricsResponse:
    """Get real-time fraud metrics."""
    now = datetime.utcnow()

    # Total transactions
    total_result = await db.execute(select(func.count()).select_from(Transaction))
    total_transactions = total_result.scalar() or 0

    # Decision distribution
    decision_query = select(
        FraudDecision.decision, func.count()
    ).group_by(FraudDecision.decision)
    decision_result = await db.execute(decision_query)
    decisions = dict(decision_result.all())

    blocked_count = decisions.get("block", 0)  # manually blocked by analyst
    escalate_count = decisions.get("escalate", 0)
    verify_count = decisions.get("verify", 0)
    approved_count = decisions.get("approve", 0)

    # Critical count: escalated with score >= 80
    critical_result = await db.execute(
        select(func.count())
        .where(FraudDecision.decision == "escalate")
        .where(FraudDecision.risk_score > 80)
    )
    critical_count = critical_result.scalar() or 0

    # Review count is escalate with score < 80
    review_count = escalate_count - critical_count

    # Fraud rate (critical + escalate / total)
    flagged = escalate_count + blocked_count
    fraud_rate = flagged / max(total_transactions, 1)

    # Average risk score
    avg_score_result = await db.execute(select(func.avg(FraudDecision.risk_score)))
    avg_risk_score = float(avg_score_result.scalar() or 0)

    # High risk count (score >= 70)
    high_risk_result = await db.execute(
        select(func.count()).where(FraudDecision.risk_score >= 70)
    )
    high_risk_count = high_risk_result.scalar() or 0

    # Total amount at risk (sum of amounts for blocked + escalated transactions)
    amount_at_risk_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .join(FraudDecision, FraudDecision.transaction_id == Transaction.transaction_id)
        .where(FraudDecision.decision.in_(["block", "escalate"]))
    )
    total_amount_at_risk = float(amount_at_risk_result.scalar() or 0)

    # Analyst review stats
    reviewed_result = await db.execute(
        select(func.count()).where(FraudDecision.analyst_action.isnot(None))
    )
    reviewed_by_analyst = reviewed_result.scalar() or 0

    pending_result = await db.execute(
        select(func.count()).where(
            and_(
                FraudDecision.decision.in_(["escalate", "verify"]),
                FraudDecision.analyst_action.is_(None),
            )
        )
    )
    pending_review = pending_result.scalar() or 0

    # Score distribution (buckets of 10)
    score_distribution = []
    for low in range(0, 100, 10):
        high = low + 10
        count_result = await db.execute(
            select(func.count()).where(
                and_(FraudDecision.risk_score >= low, FraudDecision.risk_score < high)
            )
        )
        count = count_result.scalar() or 0
        score_distribution.append({"bucket": f"{low}-{high}", "count": count})

    # Throughput (transactions in last minute)
    one_min_ago = now - timedelta(minutes=1)
    tps_result = await db.execute(
        select(func.count()).where(Transaction.created_at >= one_min_ago)
    )
    recent_count = tps_result.scalar() or 0
    throughput_tps = recent_count / 60.0

    # Recent high-risk transactions (top 10 by score)
    recent_high_risk_query = (
        select(FraudDecision, Transaction)
        .join(Transaction, FraudDecision.transaction_id == Transaction.transaction_id)
        .where(FraudDecision.risk_score > 60)
        .order_by(desc(FraudDecision.risk_score))
        .limit(10)
    )
    recent_result = await db.execute(recent_high_risk_query)
    recent_high_risk = []
    for fd, txn in recent_result.all():
        recent_high_risk.append(RecentTransaction(
            transaction_id=fd.transaction_id,
            user_id=txn.user_id,
            merchant_id=txn.merchant_id,
            amount=float(txn.amount),
            risk_score=float(fd.risk_score),
            decision=fd.decision,
            signals=fd.signals or [],
            decided_at=fd.decided_at.isoformat() if fd.decided_at else "",
            analyst_action=fd.analyst_action,
        ))

    # Top risky users (by avg risk score, min 2 transactions)
    top_users_query = (
        select(
            Transaction.user_id,
            func.count().label("txn_count"),
            func.avg(FraudDecision.risk_score).label("avg_score"),
            func.sum(Transaction.amount).label("total_amount"),
        )
        .join(FraudDecision, FraudDecision.transaction_id == Transaction.transaction_id)
        .group_by(Transaction.user_id)
        .having(func.count() >= 2)
        .order_by(desc("avg_score"))
        .limit(5)
    )
    top_users_result = await db.execute(top_users_query)
    top_risky_users = []
    for row in top_users_result.all():
        # Get their last decision
        last_decision_result = await db.execute(
            select(FraudDecision.decision)
            .join(Transaction, FraudDecision.transaction_id == Transaction.transaction_id)
            .where(Transaction.user_id == row.user_id)
            .order_by(desc(FraudDecision.decided_at))
            .limit(1)
        )
        last_decision = last_decision_result.scalar() or "unknown"
        top_risky_users.append(TopRiskyUser(
            user_id=row.user_id,
            transaction_count=row.txn_count,
            avg_risk_score=round(float(row.avg_score), 1),
            total_amount=float(row.total_amount),
            last_decision=last_decision,
        ))

    return MetricsResponse(
        total_transactions=total_transactions,
        fraud_rate=round(fraud_rate, 4),
        false_positive_rate=0.0,
        avg_risk_score=round(avg_risk_score, 2),
        avg_latency_ms=0.0,
        decisions=decisions,
        score_distribution=score_distribution,
        throughput_tps=round(throughput_tps, 2),
        critical_count=critical_count,
        blocked_count=blocked_count,
        review_count=review_count,
        verify_count=verify_count,
        approved_count=approved_count,
        high_risk_count=high_risk_count,
        total_amount_at_risk=round(total_amount_at_risk, 2),
        reviewed_by_analyst=reviewed_by_analyst,
        pending_review=pending_review,
        recent_high_risk=recent_high_risk,
        top_risky_users=top_risky_users,
    )


@router.get("/transactions")
async def get_metric_transactions(
    category: str = Query(..., description="Metric category to filter by"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get transactions for a specific metric category (drill-down)."""
    query = (
        select(FraudDecision, Transaction)
        .join(Transaction, FraudDecision.transaction_id == Transaction.transaction_id)
    )

    if category == "all":
        pass  # No filter — show all transactions
    elif category == "critical":
        query = query.where(
            and_(FraudDecision.decision == "escalate", FraudDecision.risk_score > 80)
        )
    elif category == "blocked":
        query = query.where(FraudDecision.decision == "block")
    elif category == "escalate":
        query = query.where(
            and_(FraudDecision.decision == "escalate", FraudDecision.risk_score <= 80)
        )
    elif category == "verify":
        query = query.where(FraudDecision.decision == "verify")
    elif category == "approved":
        query = query.where(FraudDecision.decision == "approve")
    elif category == "high_risk":
        query = query.where(FraudDecision.risk_score >= 70)
    elif category == "fraud_rate":
        query = query.where(FraudDecision.decision.in_(["block", "escalate"]))
    elif category == "pending":
        query = query.where(
            and_(
                FraudDecision.decision.in_(["block", "escalate", "verify"]),
                FraudDecision.analyst_action.is_(None),
            )
        )
    elif category == "reviewed":
        query = query.where(FraudDecision.analyst_action.isnot(None))
    elif category == "amount_at_risk":
        query = query.where(FraudDecision.decision.in_(["block", "escalate"]))
    else:
        pass  # Unknown category — return all

    query = query.order_by(desc(FraudDecision.risk_score)).limit(200)
    result = await db.execute(query)

    transactions = []
    for fd, txn in result.all():
        transactions.append({
            "id": str(fd.id),
            "transaction_id": fd.transaction_id,
            "user_id": txn.user_id,
            "merchant_id": txn.merchant_id,
            "amount": float(txn.amount),
            "risk_score": float(fd.risk_score),
            "decision": fd.decision,
            "signals": fd.signals or [],
            "sub_scores": fd.sub_scores or {},
            "explanation": fd.explanation or "",
            "analyst_action": fd.analyst_action,
            "decided_at": fd.decided_at.isoformat() if fd.decided_at else "",
        })

    return {"category": category, "transactions": transactions, "total": len(transactions)}
