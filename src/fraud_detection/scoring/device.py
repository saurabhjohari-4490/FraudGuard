"""Device Risk Engine - assesses device-based fraud signals. Weight: 20%."""

import time

from fraud_detection.scoring.base import ScoringModule, ScoringResult, TransactionContext


class DeviceRiskEngine(ScoringModule):
    name = "device_risk"
    weight = 0.20
    description = "Evaluates device-based risk: emulator, rooted, shared, new device"

    # Thresholds
    NEW_DEVICE_WINDOW_SECONDS = 300  # Device seen < 5 minutes ago
    SHARED_DEVICE_THRESHOLD = 3     # More than 3 users on same device

    async def score(self, context: TransactionContext) -> ScoringResult:
        signals: list[str] = []
        score = 0.0
        enrichment = context.enrichment

        if not context.device_fingerprint:
            # No device info - moderate risk
            score += 15
            signals.append("No device fingerprint provided")
            return ScoringResult(score=score, confidence=0.4, signals=signals)

        # Emulator detection
        if enrichment.device_is_emulator:
            score += 40
            signals.append("Transaction from emulator/virtual device")

        # Rooted/jailbroken device
        if enrichment.device_is_rooted:
            score += 30
            signals.append("Transaction from rooted/jailbroken device")

        # New device (never seen before or very recently)
        if enrichment.device_first_seen > 0:
            device_age_seconds = time.time() - enrichment.device_first_seen
            if device_age_seconds < self.NEW_DEVICE_WINDOW_SECONDS:
                score += 25
                signals.append(f"New device (first seen {int(device_age_seconds)}s ago)")
            elif device_age_seconds < 3600:
                score += 10
                signals.append("Recently registered device (< 1 hour)")
        else:
            score += 20
            signals.append("First time seeing this device")

        # Shared device (multiple users)
        if enrichment.device_user_count >= self.SHARED_DEVICE_THRESHOLD:
            score += 25
            signals.append(
                f"Shared device: {enrichment.device_user_count} different users"
            )
        elif enrichment.device_user_count == 2:
            score += 10
            signals.append("Device used by 2 different users")

        # Combine emulator + rooted (extra dangerous)
        if enrichment.device_is_emulator and enrichment.device_is_rooted:
            score += 15
            signals.append("Emulator AND rooted - high risk combination")

        confidence = 0.85

        return ScoringResult(
            score=min(100.0, score),
            confidence=confidence,
            signals=signals,
            metadata={
                "is_emulator": enrichment.device_is_emulator,
                "is_rooted": enrichment.device_is_rooted,
                "user_count": enrichment.device_user_count,
            },
        )
