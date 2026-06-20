"""Full fraud detection pipeline - orchestrates enrich → score → decide → store."""

import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from fraud_detection.dependencies import get_enrichment_service
from fraud_detection.models.fraud_decision import FraudDecision
from fraud_detection.schemas.transaction import TransactionCreate
from fraud_detection.scoring.base import TransactionContext
from fraud_detection.services.decision_engine import DecisionEngine, FraudDecisionResult
from fraud_detection.services.risk_aggregator import RiskAggregator
from fraud_detection.services.scoring_pipeline import create_default_pipeline

logger = logging.getLogger(__name__)

# Module-level singletons
_pipeline = create_default_pipeline()
_aggregator = RiskAggregator()
_decision_engine = DecisionEngine()


async def run_fraud_pipeline(
    transaction: TransactionCreate, db: AsyncSession
) -> FraudDecisionResult:
    """Execute the complete fraud detection pipeline.

    Steps:
    1. Enrich transaction with velocity, user profile, device features
    2. Score via all 6 modules in parallel
    3. Aggregate scores with weights
    4. Make decision based on thresholds
    5. Store decision in database
    """
    # Step 1: Enrich
    enrichment_service = get_enrichment_service()
    enrichment = await enrichment_service.enrich(
        user_id=transaction.user_id,
        device_fingerprint=transaction.device_fingerprint,
        amount=float(transaction.amount),
    )

    # Step 2: Build scoring context
    context = TransactionContext(
        transaction_id=transaction.transaction_id,
        user_id=transaction.user_id,
        merchant_id=transaction.merchant_id,
        amount=transaction.amount,
        currency=transaction.currency,
        card_bin=transaction.card_bin,
        device_fingerprint=transaction.device_fingerprint,
        ip_address=transaction.ip_address,
        geo_lat=transaction.geo_lat,
        geo_lon=transaction.geo_lon,
        channel=transaction.channel,
        timestamp=transaction.timestamp,
        metadata=transaction.metadata,
        enrichment=enrichment,
    )

    # Step 3: Score
    scores = await _pipeline.execute(context)

    # Step 4: Aggregate
    aggregated = _aggregator.aggregate(scores)

    # Step 5: Decide
    result = _decision_engine.decide(aggregated)

    # Step 6: Store decision
    decision_record = FraudDecision(
        id=uuid.uuid4(),
        transaction_id=transaction.transaction_id,
        risk_score=result.risk_score,
        decision=result.decision,
        sub_scores=result.sub_scores,
        signals=result.signals,
        explanation=result.explanation,
    )
    db.add(decision_record)

    # Step 7: Update user profile ONLY if approved
    # Fraudulent transactions must NOT alter the user's baseline — otherwise
    # a single large fraud txn permanently inflates avg_amount, making future
    # fraud look "normal" by comparison.
    if result.decision == "approve":
        await enrichment_service.update_profile_on_approve(
            user_id=transaction.user_id,
            device_fingerprint=transaction.device_fingerprint,
            amount=float(transaction.amount),
            merchant_id=transaction.merchant_id,
        )

    logger.info(
        f"Pipeline complete: txn={transaction.transaction_id} "
        f"score={result.risk_score:.1f} decision={result.decision} "
        f"enrichment_ms={enrichment.enrichment_time_ms:.1f}"
    )

    return result
