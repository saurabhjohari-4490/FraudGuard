"""Explainability Service - generates human-readable fraud decision explanations."""

TEMPLATES: dict[str, str] = {
    "approve": (
        "Transaction approved. Risk score {score:.1f}/100. "
        "No significant fraud indicators detected."
    ),
    "verify": (
        "Additional verification required. Risk score {score:.1f}/100. "
        "Key concerns: {top_signals}."
    ),
    "escalate": (
        "Queued for analyst review. Risk score {score:.1f}/100. "
        "{signal_count} fraud signal(s) detected: {top_signals}."
    ),
    "escalate_critical": (
        "CRITICAL RISK - Immediate analyst action required. Risk score {score:.1f}/100. "
        "Multiple critical fraud indicators: {top_signals}."
    ),
    "block": (
        "Transaction blocked by analyst. Risk score {score:.1f}/100. "
        "Confirmed fraud indicators: {top_signals}."
    ),
}

MODULE_NAMES: dict[str, str] = {
    "behavior_analyzer": "Behavior Analysis",
    "velocity_detector": "Velocity Detection",
    "device_risk": "Device Risk",
    "merchant_risk": "Merchant Risk",
    "geolocation": "Geolocation",
    "ip_intelligence": "IP Intelligence",
}


class ExplainabilityService:
    """Generates human-readable explanations for fraud decisions."""

    def explain(
        self,
        decision: str,
        score: float,
        signals: list[str],
        sub_scores: dict[str, float],
        risk_level: str = "",
    ) -> str:
        """Generate explanation text for a fraud decision."""
        top_signals = "; ".join(signals[:3]) if signals else "None detected"

        # Use critical template for high-risk escalations
        if decision == "escalate" and risk_level == "critical":
            template = TEMPLATES["escalate_critical"]
        else:
            template = TEMPLATES.get(decision, TEMPLATES["escalate"])

        explanation = template.format(
            score=score,
            top_signals=top_signals,
            signal_count=len(signals),
        )

        # Add top contributing module if score is high enough
        if score > 30 and sub_scores:
            top_module = max(sub_scores, key=sub_scores.get)  # type: ignore
            module_label = MODULE_NAMES.get(top_module, top_module)
            explanation += f" Primary risk driver: {module_label} (score: {sub_scores[top_module]:.0f})."

        return explanation
