"""Decision Engine - maps risk scores to fraud decisions."""

from dataclasses import dataclass
from enum import Enum

from fraud_detection.services.explainability import ExplainabilityService
from fraud_detection.services.risk_aggregator import AggregatedRisk


class Decision(str, Enum):
    APPROVE = "approve"
    VERIFY = "verify"
    ESCALATE = "escalate"
    BLOCK = "block"


@dataclass
class FraudDecisionResult:
    """Final fraud decision with all context."""

    decision: str
    risk_score: float
    sub_scores: dict[str, float]
    signals: list[str]
    explanation: str
    risk_level: str = ""  # critical, high, medium, low


class DecisionEngine:
    """Maps aggregated risk scores to actionable decisions.

    Thresholds:
        0-30:  APPROVE (auto-approve)
        31-60: VERIFY  (request additional verification)
        61-100: ESCALATE (queue for analyst review; 80+ tagged as critical risk)

    Note: BLOCK is never assigned automatically. It is a manual-only
    analyst action to confirm fraud and halt the transaction.
    """

    THRESHOLDS = [
        (30, Decision.APPROVE),
        (60, Decision.VERIFY),
        (100, Decision.ESCALATE),
    ]

    def __init__(self, explainability: ExplainabilityService | None = None) -> None:
        self._explainability = explainability or ExplainabilityService()

    @staticmethod
    def compute_risk_level(score: float) -> str:
        """Compute risk level tag from score.

        Aligned with decision thresholds:
            0-30 (approve)  → low
            31-60 (verify)  → medium
            61-80 (escalate) → high
            81-100 (escalate+critical) → critical
        """
        if score > 80:
            return "critical"
        if score > 60:
            return "high"
        if score > 30:
            return "medium"
        return "low"

    def decide(self, aggregated: AggregatedRisk) -> FraudDecisionResult:
        """Make a fraud decision based on the aggregated risk score."""
        decision = Decision.ESCALATE  # default to safest (never auto-block)
        for threshold, d in self.THRESHOLDS:
            if aggregated.total_score <= threshold:
                decision = d
                break

        risk_level = self.compute_risk_level(aggregated.total_score)

        explanation = self._explainability.explain(
            decision=decision.value,
            score=aggregated.total_score,
            signals=aggregated.signals,
            sub_scores=aggregated.sub_scores,
            risk_level=risk_level,
        )

        return FraudDecisionResult(
            decision=decision.value,
            risk_score=aggregated.total_score,
            sub_scores=aggregated.sub_scores,
            signals=aggregated.signals,
            explanation=explanation,
            risk_level=risk_level,
        )
