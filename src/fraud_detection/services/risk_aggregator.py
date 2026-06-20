"""Risk Aggregator - combines module scores with weighted formula."""

from dataclasses import dataclass, field

from fraud_detection.scoring.base import ScoringResult

# Scoring module weights (must sum to 1.0)
WEIGHTS: dict[str, float] = {
    "behavior_analyzer": 0.25,
    "velocity_detector": 0.20,
    "device_risk": 0.20,
    "merchant_risk": 0.15,
    "geolocation": 0.10,
    "ip_intelligence": 0.10,
}


@dataclass
class AggregatedRisk:
    """Final aggregated risk assessment."""

    total_score: float  # 0-100
    sub_scores: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    signals: list[str] = field(default_factory=list)


class RiskAggregator:
    """Combines individual module scores into a single risk score."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self._weights = weights or WEIGHTS

    def aggregate(self, scores: dict[str, ScoringResult]) -> AggregatedRisk:
        """Aggregate module scores using weighted formula with signal boosts.

        Base score = sum(module_score * module_weight) for all modules.

        Critical signal boost: if any module scores >= 80, the total score
        is raised to at least 60% of the highest module score. This prevents
        a single extreme fraud signal from being diluted by quiet modules.

        Multi-module amplifier: when multiple modules (>= 3) each score >= 20,
        it indicates broad fraud signal coverage across dimensions. A multiplier
        is applied: 3 active → 1.2x, 4 active → 1.4x, 5+ active → 1.6x.
        This ensures transactions triggering most modules get critical-level scores.
        """
        total = 0.0
        weighted_confidence = 0.0
        sub_scores: dict[str, float] = {}
        all_signals: list[str] = []
        max_module_score = 0.0
        active_module_count = 0

        for module_name, weight in self._weights.items():
            result = scores.get(module_name)
            if result:
                total += result.score * weight
                weighted_confidence += result.confidence * weight
                sub_scores[module_name] = round(result.score, 2)
                all_signals.extend(result.signals)
                max_module_score = max(max_module_score, result.score)
                if result.score >= 20:
                    active_module_count += 1
            else:
                sub_scores[module_name] = 0.0

        # Critical signal boost: extreme individual scores raise the floor
        if max_module_score >= 80:
            floor = max_module_score * 0.6
            total = max(total, floor)

        # Multi-module amplifier: broad fraud coverage across dimensions
        if active_module_count >= 5:
            total *= 1.6
        elif active_module_count >= 4:
            total *= 1.4
        elif active_module_count >= 3:
            total *= 1.2

        # Cap score at 0-100
        total_score = max(0.0, min(100.0, total))

        return AggregatedRisk(
            total_score=round(total_score, 2),
            sub_scores=sub_scores,
            confidence=round(weighted_confidence, 3),
            signals=all_signals,
        )
