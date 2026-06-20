"""Merchant Risk Engine - evaluates merchant category and fraud rate. Weight: 15%."""

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext

# High-risk merchant categories and their base risk scores
HIGH_RISK_CATEGORIES: dict[str, float] = {
    "gambling": 30,
    "crypto": 25,
    "adult": 20,
    "digital_goods": 15,
    "travel": 10,
    "electronics": 10,
}

# Known high-fraud-rate merchant patterns
SUSPICIOUS_MERCHANT_PATTERNS = [
    "test_",
    "demo_",
    "temp_",
]


class MerchantRiskEngine(ScoringModule):
    name = "merchant_risk"
    weight = 0.15
    description = "Evaluates merchant category risk and fraud association"

    async def score(self, context: TransactionContext) -> ScoringResult:
        signals: list[str] = []
        score = 0.0

        merchant_id = context.merchant_id.lower()

        # Check suspicious merchant name patterns
        for pattern in SUSPICIOUS_MERCHANT_PATTERNS:
            if merchant_id.startswith(pattern):
                score += 20
                signals.append(f"Suspicious merchant name pattern: {pattern}")
                break

        # Check merchant category from metadata
        category = context.metadata.get("merchant_category", "").lower()
        if category in HIGH_RISK_CATEGORIES:
            cat_score = HIGH_RISK_CATEGORIES[category]
            score += cat_score
            signals.append(f"High-risk merchant category: {category}")

        # First-time merchant for this user (from enrichment)
        if (
            context.enrichment.user_typical_merchants
            and context.merchant_id not in context.enrichment.user_typical_merchants
        ):
            score += 10
            signals.append("New merchant for this user")

        # High amount at high-risk merchant
        amount = float(context.amount)
        if category in HIGH_RISK_CATEGORIES and amount > 50000:
            score += 15
            signals.append("Large transaction at high-risk merchant")

        # Cross-border indicator
        if context.metadata.get("cross_border"):
            score += 10
            signals.append("Cross-border merchant transaction")

        confidence = 0.7  # Merchant risk is contextual

        return ScoringResult(
            score=min(100.0, score),
            confidence=confidence,
            signals=signals,
            metadata={"category": category, "merchant_id": context.merchant_id},
        )
