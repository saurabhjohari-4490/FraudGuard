"""Behavior Analyzer - detects spending anomalies vs user history. Weight: 25%."""

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext


class BehaviorAnalyzer(ScoringModule):
    name = "behavior_analyzer"
    weight = 0.25
    description = "Analyzes transaction patterns against user historical behavior"

    async def score(self, context: TransactionContext) -> ScoringResult:
        signals: list[str] = []
        score = 0.0
        enrichment = context.enrichment

        # Amount deviation from user average
        if enrichment.user_avg_amount and enrichment.user_avg_amount > 0:
            ratio = float(context.amount) / enrichment.user_avg_amount
            if ratio > 50.0:
                score += 80
                signals.append(f"Amount is {ratio:.1f}x higher than user average - extreme anomaly")
            elif ratio > 10.0:
                score += 60
                signals.append(f"Amount is {ratio:.1f}x higher than user average")
            elif ratio > 5.0:
                score += 40
                signals.append(f"Amount is {ratio:.1f}x higher than user average")
            elif ratio > 3.0:
                score += 20
                signals.append(f"Amount is {ratio:.1f}x above user average")
        elif enrichment.user_txn_count == 0:
            # First-time user gets a small risk bump
            score += 10
            signals.append("First transaction for this user")

        # New merchant for user
        if (
            enrichment.user_typical_merchants
            and context.merchant_id not in enrichment.user_typical_merchants
        ):
            score += 15
            signals.append("First transaction with this merchant")

        # Time-of-day anomaly
        hour = context.timestamp.hour
        if 1 <= hour <= 5:
            score += 20
            signals.append(f"Transaction during unusual hours ({hour}:00)")
        elif 0 <= hour <= 1 or 22 <= hour <= 23:
            score += 10
            signals.append("Late night transaction")

        # Large round amounts (common in fraud)
        amount_float = float(context.amount)
        if amount_float >= 10000 and amount_float % 1000 == 0:
            score += 10
            signals.append("Large round amount")

        # Confidence based on user history depth
        confidence = min(1.0, enrichment.user_txn_count / 20.0) if enrichment.user_txn_count > 0 else 0.3

        return ScoringResult(
            score=min(100.0, score),
            confidence=confidence,
            signals=signals,
            metadata={"amount_ratio": float(context.amount) / max(enrichment.user_avg_amount, 1)},
        )
