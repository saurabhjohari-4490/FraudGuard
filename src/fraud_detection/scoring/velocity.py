"""Velocity Detector - detects transaction bursts. Weight: 20%."""

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext


class VelocityDetector(ScoringModule):
    name = "velocity_detector"
    weight = 0.20
    description = "Detects unusual transaction frequency and velocity bursts"

    # Thresholds
    BURST_1M = 3      # More than 3 txns in 1 minute is suspicious
    BURST_5M = 8      # More than 8 txns in 5 minutes
    BURST_1H = 20     # More than 20 txns in 1 hour
    HIGH_VOLUME_24H = 50  # More than 50 txns in 24 hours

    async def score(self, context: TransactionContext) -> ScoringResult:
        signals: list[str] = []
        score = 0.0
        enrichment = context.enrichment

        # 1-minute burst (most critical)
        if enrichment.velocity_1m >= self.BURST_1M:
            burst_score = min(70, (enrichment.velocity_1m - self.BURST_1M + 1) * 20)
            score += burst_score
            signals.append(f"Velocity burst: {enrichment.velocity_1m} txns in last 1 minute")

        # 5-minute burst
        if enrichment.velocity_5m >= self.BURST_5M:
            burst_score = min(50, (enrichment.velocity_5m - self.BURST_5M + 1) * 12)
            score += burst_score
            signals.append(f"High velocity: {enrichment.velocity_5m} txns in last 5 minutes")

        # 1-hour volume
        if enrichment.velocity_1h >= self.BURST_1H:
            score += 20
            signals.append(f"Elevated volume: {enrichment.velocity_1h} txns in last hour")

        # 24-hour volume
        if enrichment.velocity_24h >= self.HIGH_VOLUME_24H:
            score += 15
            signals.append(f"High daily volume: {enrichment.velocity_24h} txns in 24h")

        # Acceleration pattern (5m count is disproportionately high vs 1h)
        if enrichment.velocity_1h > 0:
            acceleration = enrichment.velocity_5m / (enrichment.velocity_1h / 12)
            if acceleration > 3.0:
                score += 15
                signals.append("Rapid acceleration in transaction rate")

        confidence = 0.9  # Velocity is a reliable signal

        return ScoringResult(
            score=min(100.0, score),
            confidence=confidence,
            signals=signals,
            metadata={
                "vel_1m": enrichment.velocity_1m,
                "vel_5m": enrichment.velocity_5m,
                "vel_1h": enrichment.velocity_1h,
                "vel_24h": enrichment.velocity_24h,
            },
        )
