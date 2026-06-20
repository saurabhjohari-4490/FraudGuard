"""Transaction API endpoints."""

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from fraud_detection.db.session import get_db
from fraud_detection.models.transaction import Transaction
from fraud_detection.models.fraud_decision import FraudDecision
from fraud_detection.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionListResponse,
    TransactionResponse,
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("", status_code=201, response_model=TransactionResponse)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    """Ingest a transaction, run fraud scoring pipeline, and return decision."""
    start = time.perf_counter()

    # Check for duplicate transaction_id
    existing = await db.execute(
        select(Transaction).where(Transaction.transaction_id == payload.transaction_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Transaction already exists")

    # Store transaction
    txn = Transaction(
        id=uuid.uuid4(),
        transaction_id=payload.transaction_id,
        user_id=payload.user_id,
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        currency=payload.currency,
        card_bin=payload.card_bin,
        device_fingerprint=payload.device_fingerprint,
        ip_address=payload.ip_address,
        geo_lat=payload.geo_lat,
        geo_lon=payload.geo_lon,
        channel=payload.channel,
        extra_data=payload.metadata,
    )
    db.add(txn)
    await db.flush()

    # Import scoring pipeline (lazy to avoid circular imports)
    from fraud_detection.services.pipeline import run_fraud_pipeline

    result = await run_fraud_pipeline(payload, db)

    processing_time = (time.perf_counter() - start) * 1000
    return TransactionResponse(
        transaction_id=payload.transaction_id,
        risk_score=result.risk_score,
        decision=result.decision,
        risk_level=result.risk_level,
        signals=result.signals,
        explanation=result.explanation,
        processing_time_ms=round(processing_time, 2),
    )


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    q: str | None = None,
    user_id: str | None = None,
    merchant_id: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    """Search and list transactions with filters."""
    query = select(Transaction).order_by(Transaction.created_at.desc())

    if user_id:
        query = query.where(Transaction.user_id == user_id)
    if merchant_id:
        query = query.where(Transaction.merchant_id == merchant_id)
    if q:
        query = query.where(
            or_(
                Transaction.transaction_id.ilike(f"%{q}%"),
                Transaction.user_id.ilike(f"%{q}%"),
                Transaction.merchant_id.ilike(f"%{q}%"),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    offset = (page - 1) * limit
    results = await db.execute(query.offset(offset).limit(limit))
    transactions = results.scalars().all()

    # Get associated decisions
    txn_ids = [t.transaction_id for t in transactions]
    decisions_result = await db.execute(
        select(FraudDecision).where(FraudDecision.transaction_id.in_(txn_ids))
    )
    decisions_map = {d.transaction_id: d for d in decisions_result.scalars().all()}

    items = []
    for t in transactions:
        decision = decisions_map.get(t.transaction_id)
        items.append(
            TransactionDetail(
                transaction_id=t.transaction_id,
                user_id=t.user_id,
                merchant_id=t.merchant_id,
                amount=float(t.amount),
                currency=t.currency,
                device_fingerprint=t.device_fingerprint,
                ip_address=str(t.ip_address) if t.ip_address else None,
                geo_lat=t.geo_lat,
                geo_lon=t.geo_lon,
                channel=t.channel,
                created_at=t.created_at,
                risk_score=float(decision.risk_score) if decision else None,
                decision=decision.decision if decision else None,
            )
        )

    return TransactionListResponse(
        transactions=items, total=total, page=page, page_size=limit
    )
